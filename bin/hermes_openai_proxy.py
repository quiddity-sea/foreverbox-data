from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import subprocess
import json
import uuid
import os

app = FastAPI(title="ForeverBox Hermes Gateway", version="2.0")

VALID_PROFILES = {"zeon7", "leon", "gemma", "otec", "wolf"}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    if not messages:
        return JSONResponse({"error": "No messages supplied"}, status_code=400)
    
    last_message = messages[-1]["content"] if messages[-1]["role"] == "user" else "Hello"
    
    # 1. Resolve Target Agent Profile
    raw_model = str(data.get("model", "zeon7")).lower().strip()
    profile = raw_model if raw_model in VALID_PROFILES else "zeon7"
    
    # 2. Check for optional Model & Provider runtime overrides
    override_model = data.get("override_model")
    override_provider = data.get("override_provider")
    
    hermes_bin = "/foreverbox_data/venv/bin/hermes"
    if not os.path.exists(hermes_bin):
        hermes_bin = "hermes"

    cmd = [
        hermes_bin,
        "--profile", profile,
        "chat",
        "-Q", "--yolo", "--accept-hooks",
        "--query", last_message
    ]
    
    # Only append -m if a non-empty model string was provided
    if override_model and str(override_model).strip():
        cmd.extend(["-m", str(override_model).strip()])
        
    # Map provider alias if provided
    if override_provider and str(override_provider).strip():
        prov = str(override_provider).strip().lower()
        if prov == "ollama":
            prov = "custom:g4"
        cmd.extend(["--provider", prov])
        
    env = os.environ.copy()
    env_file = os.path.expanduser("~/.hermes/.env")
    if not os.path.exists(env_file):
        env_file = "/home/zeon7/.hermes/.env"
    if os.path.exists(env_file):
        try:
            with open(env_file, "r") as ef:
                for line in ef:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip()
        except Exception:
            pass

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=280
        )
        reply = result.stdout.strip()
    except subprocess.TimeoutExpired:
        reply = f"Error: Hermes execution for agent '{profile}' exceeded 280-second timeout."
    except subprocess.CalledProcessError as e:
        combined = f"{e.stderr}\n{e.stdout}".strip()
        lines = [l for l in combined.splitlines() if not l.strip().startswith("session_id:")]
        clean_err = "\n".join(lines).strip() or combined
        reply = f"Error from Hermes ({profile}): {clean_err}"
    except Exception as e:
        reply = f"System Gateway Error ({profile}): {str(e)}"
    
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": 1234567890,
        "model": profile,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": reply
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8081)
