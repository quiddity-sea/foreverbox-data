"""
qwen_proxy: Translation layer between Hermes and Qwen 2.5 on Ollama.

Listens on port 11435, forwards to Ollama on port 11434.
Intercepts /v1/chat/completions to:

1. Strip the `tools` array from the request (Qwen 2.5 doesn't generate
   proper OpenAI tool_calls — it embeds JSON in the content field with
   names derived from descriptions, not the actual function names).

2. Inject a system-prompt appendix that describes each tool by its exact
   name, parameters, and the JSON format to use.

3. On the response, scan the content for embedded tool-call JSON objects,
   extract them into proper OpenAI tool_calls format, and scrub them from
   the content text.

Result: Hermes sees a model that speaks perfect OpenAI function calling.
Qwen just outputs structured JSON text. The proxy bridges the gap.

No modelfiles, no fine-tuning, no Hermes config hacks.
"""

import json
import logging
import uuid
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_HOST = "http://localhost:11434"
PROXY_PORT = 11435

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("qwen_proxy")

app = FastAPI(title="Qwen Proxy")

stats = {"requests": 0, "tool_calls_translated": 0, "injections": 0, "streaming_chunks": 0}


# ---------------------------------------------------------------------------
# System-prompt injection: convert Hermes' tools array into natural language
# instructions that Qwen can follow.
# ---------------------------------------------------------------------------

def build_tool_system_prompt(tools: list) -> str:
    """Build a system-prompt appendix describing each tool in exact detail."""
    lines = [
        "\n\n## Available Tools",
        "",
        "When you need to perform an action, you MUST output a JSON object",
        "with exactly this format (no extra text around it):",
        '',
        '{"name": "<tool_name>", "arguments": {<parameters>}}',
        "",
        "Here are the tools you can use:",
    ]

    for tool in tools:
        fn = tool.get("function", tool)
        name = fn.get("name", "unknown")
        description = fn.get("description", "")
        params = fn.get("parameters", {}).get("properties", {})
        required = fn.get("parameters", {}).get("required", [])

        lines.append("")
        lines.append(f"---")
        lines.append(f"Tool: {name}")
        if description:
            lines.append(f"  Description: {description}")
        lines.append(f"  JSON format:")
        lines.append(f'    {{"name": "{name}", "arguments": {{')

        param_lines = []
        for pname, pinfo in params.items():
            ptype = pinfo.get("type", "string")
            pdesc = pinfo.get("description", "")
            is_req = " (required)" if pname in required else ""
            param_lines.append(f'      "{pname}": <{ptype}>{is_req} — {pdesc}')

        if param_lines:
            lines.append("\n".join(param_lines))
        else:
            lines.append("      (no parameters)")

        lines.append("    }}")

    lines.append("")
    lines.append(
        "IMPORTANT: Use the EXACT tool name shown above. "
        "Output ONE JSON object per tool call. "
        "You may output multiple JSON objects if you need to call multiple tools."
    )
    lines.append(
        "After the tool executes, you will see the result. "
        "Continue the conversation normally."
    )

    return "\n".join(lines)


def inject_tool_prompt(messages: list, tools: list, tool_prompt: str) -> list:
    """Inject the tool description prompt into the messages array.

    Appends to the existing system message if there is one;
    otherwise prepends a new system message.
    """
    if not messages:
        messages = []

    # Find the first system message
    for msg in messages:
        if msg.get("role") == "system":
            msg["content"] = (msg.get("content", "") or "") + tool_prompt
            return messages

    # No system message found — prepend one
    messages.insert(0, {"role": "system", "content": tool_prompt.strip()})
    return messages


# ---------------------------------------------------------------------------
# Tool-call extraction helpers
# ---------------------------------------------------------------------------

def extract_tool_json_objects(text: str):
    """Scan text for JSON objects with 'name' and 'arguments' keys.

    Uses json.JSONDecoder.raw_decode to properly handle nested objects
    (e.g. arguments with nested dicts). Returns list of (start, end, parsed_dict).
    """
    decoder = json.JSONDecoder()
    results = []
    idx = 0
    while idx < len(text):
        c = text[idx]
        if c not in ("{", "[", '"', "'", "`"):
            idx += 1
            continue
        try:
            obj, end = decoder.raw_decode(text, idx)
            if isinstance(obj, dict) and "name" in obj and "arguments" in obj:
                results.append((idx, end, obj))
            idx = end
        except (json.JSONDecodeError, ValueError):
            idx += 1
    return results


def build_tool_calls(found_calls, known_tool_names: set | None = None):
    """Convert extracted tool-call dicts into OpenAI tool_calls array.

    If known_tool_names is provided, only include calls whose name
    appears in that set (after a case-insensitive comparison).
    """
    tool_calls = []
    for _, _, obj in found_calls:
        name = obj["name"]

        # Fuzzy-match against known names if provided
        if known_tool_names and name not in known_tool_names:
            # Try case-insensitive match
            matched = False
            for known in known_tool_names:
                if name.lower() == known.lower():
                    name = known
                    matched = True
                    break
            if not matched:
                log.warning("Unknown tool name '%s' — skipping", name)
                continue

        tool_calls.append({
            "id": f"call_{uuid.uuid4().hex[:24]}",
            "type": "function",
            "function": {
                "name": name,
                "arguments": json.dumps(obj["arguments"], ensure_ascii=False),
            },
        })

    return tool_calls


def remove_tool_json_from_text(text: str, found_calls) -> str:
    """Strip embedded tool-call JSON from text, preserving surrounding content.

    Also strips enclosing ```json / ``` code blocks that Qwen sometimes wraps
    around the JSON.
    """
    result = text
    for start, end, _ in sorted(found_calls, reverse=True):
        result = result[:start] + result[end:]
    # Strip leftover markdown code-block fences (handle nested stripping)
    result = result.strip()
    while result.startswith("```") or result.endswith("```"):
        result = result.removeprefix("```json").removeprefix("```").strip()
        result = result.removesuffix("```").strip()
    # Empty or noise-only
    if not result or result in (".", "!", "?", ",", ";", ":", "`"):
        return ""
    return result


# ---------------------------------------------------------------------------
# Non-streaming response handler
# ---------------------------------------------------------------------------

def process_non_streaming(
    ollama_body: bytes,
    ollama_status: int,
    known_tool_names: set | None = None,
) -> dict:
    """Process a non-streaming Ollama response, transforming tool JSON."""
    result = json.loads(ollama_body)

    if ollama_status != 200:
        return result

    choices = result.get("choices", [])
    if not choices:
        return result

    choice = choices[0]
    message = choice.get("message", {})
    content = message.get("content", "")

    if not content:
        return result

    found = extract_tool_json_objects(content)
    if not found:
        return result

    tool_calls = build_tool_calls(found, known_tool_names)
    if not tool_calls:
        return result

    cleaned = remove_tool_json_from_text(content, found)

    message["content"] = cleaned
    message["tool_calls"] = tool_calls
    message["role"] = "assistant"
    choice["finish_reason"] = "tool_calls"

    stats["tool_calls_translated"] += len(tool_calls)

    return result


# ---------------------------------------------------------------------------
# Streaming response handler — SSE chunk transformer
# ---------------------------------------------------------------------------

async def stream_through_with_translation(
    ollama_response: httpx.Response,
    known_tool_names: set | None = None,
) -> AsyncIterator[bytes]:
    """Read Ollama SSE stream, buffer content, detect tool JSON at finish.

    Qwen streams one character per SSE event and uses `finish_reason: "stop"`
    even for tool calls. We buffer all content deltas, then at the end run
    the same detection logic as the non-streaming path. If tool JSON is
    found, emit proper tool_call events instead of content.
    """
    buffered = ""
    finish_reason = None

    async for raw_line in ollama_response.aiter_lines():
        stats["streaming_chunks"] += 1

        if not raw_line.startswith("data: "):
            yield (raw_line + "\n").encode()
            continue

        payload = raw_line[6:].strip()

        if payload == "[DONE]":
            # All content accumulated. Run detection.
            found = extract_tool_json_objects(buffered)
            if found:
                tool_calls = build_tool_calls(found, known_tool_names)
                if tool_calls:
                    # Emit tool_calls as a single SSE event
                    yield _make_tool_call_chunk(
                        tool_calls[0]["function"]["name"],
                        json.loads(tool_calls[0]["function"]["arguments"]),
                    ).encode()
                    yield "data: [DONE]\n\n".encode()
                    stats["tool_calls_translated"] += len(tool_calls)
                    continue

            # No tool JSON — flush buffered content
            if buffered:
                yield (
                    'data: {"choices":[{"index":0,"delta":{"role":"assistant"}}]}\n\n'
                ).encode()
                yield _make_content_chunk(buffered).encode()
            yield (raw_line + "\n").encode()
            continue

        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            yield (raw_line + "\n").encode()
            continue

        choices = chunk.get("choices", [])
        if not choices:
            yield (raw_line + "\n").encode()
            continue

        delta = choices[0].get("delta", {})
        content = delta.get("content", "")

        # Track finish_reason from Ollama
        fr = choices[0].get("finish_reason")
        if fr:
            finish_reason = fr

        if content:
            buffered += content
            # Don't forward anything yet — buffer until we know it's not a tool call
            continue

        # Non-content events (role assignment, etc.) — pass through
        yield (raw_line + "\n").encode()
    yield "data: [DONE]\n\n".encode()


def _make_content_chunk(text: str) -> str:
    """Build an SSE data line with content delta."""
    chunk = {
        "choices": [{"index": 0, "delta": {"content": text}}]
    }
    return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"


def _make_tool_call_chunk(name: str, arguments: dict, index: int = 0) -> str:
    """Build an SSE data line with tool_calls delta."""
    chunk = {
        "choices": [{
            "index": 0,
            "delta": {
                "tool_calls": [{
                    "index": index,
                    "id": f"call_{uuid.uuid4().hex[:24]}",
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(arguments, ensure_ascii=False),
                    },
                }],
            },
            "finish_reason": "tool_calls",
        }]
    }
    return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """Intercept /v1/chat/completions to handle tool-call translation."""
    body = await request.body()
    data = json.loads(body)
    is_stream = data.get("stream", False)
    tools = data.get("tools", [])
    known_tool_names = {t.get("function", t).get("name", "") for t in tools}

    stats["requests"] += 1

    # If tools are present, strip them and inject a system prompt
    if tools:
        tool_prompt = build_tool_system_prompt(tools)
        data["messages"] = inject_tool_prompt(data.get("messages", []), tools, tool_prompt)
        del data["tools"]
        stats["injections"] += 1
        log.info(
            "Injected tool prompt for %d tools into system message | names=%s",
            len(tools),
            known_tool_names,
        )

    log.info(
        "chat_completions | stream=%s | messages=%d",
        is_stream,
        len(data.get("messages", [])),
    )

    if is_stream:
        # Streaming path: keep the HTTPX client alive for the generator's lifetime
        client = httpx.AsyncClient(timeout=300.0)
        ollama_response = await client.post(
            f"{OLLAMA_HOST}/v1/chat/completions",
            json=data,
            headers={"Content-Type": "application/json"},
        )

        if ollama_response.status_code != 200:
            await client.aclose()
            body_bytes = await ollama_response.aread()
            return Response(
                content=body_bytes,
                status_code=ollama_response.status_code,
                media_type="application/json",
            )

        async def stream_generator():
            try:
                async for chunk in stream_through_with_translation(ollama_response, known_tool_names):
                    yield chunk
            finally:
                await client.aclose()

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "cache-control": "no-cache",
                "connection": "keep-alive",
                "x-accel-buffering": "no",
            },
        )

    # Non-streaming path: use a context manager (self-contained)
    async with httpx.AsyncClient(timeout=300.0) as client:
        ollama_response = await client.post(
            f"{OLLAMA_HOST}/v1/chat/completions",
            json=data,
            headers={"Content-Type": "application/json"},
        )
        result = process_non_streaming(
            await ollama_response.aread(),
            ollama_response.status_code,
            known_tool_names,
        )
        return Response(
            content=json.dumps(result, ensure_ascii=False),
            media_type="application/json",
            status_code=ollama_response.status_code,
        )


@app.get("/health")
async def health():
    """Health check with stats."""
    return {
        "status": "ok",
        "proxy_port": PROXY_PORT,
        "upstream": OLLAMA_HOST,
        "stats": stats,
    }


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_all(path: str, request: Request):
    """Proxy all other Ollama endpoints transparently."""
    body = await request.body()
    query = request.url.query
    url = f"{OLLAMA_HOST}/{path}"
    if query:
        url += f"?{query}"

    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "transfer-encoding")
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.request(
            method=request.method,
            url=url,
            content=body,
            headers=headers,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type") or "application/json",
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    log.info("Starting Qwen Proxy on port %d → %s", PROXY_PORT, OLLAMA_HOST)
    uvicorn.run(app, host="0.0.0.0", port=PROXY_PORT, log_level="info")
