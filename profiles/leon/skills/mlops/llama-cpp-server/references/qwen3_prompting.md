# Qwen3 Prompting Best Practices

## Reasoning Behavior

Qwen3 models (including Qwen3-8B, Qwen3-14B, Qwen3-32B) **output reasoning by default** in a `reasoning_content` field separate from the main `content` field. This is a model-level default, not a server setting.

### Default Behavior
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "",
      "reasoning_content": "Okay, the user said 'hello'. I need to respond in a friendly and professional manner..."
    }
  }]
}
```

The `content` field may be empty while `reasoning_content` contains the actual response.

## Disabling Reasoning

### Method 1: System Prompt (Recommended)
Add this system message as the first message:

```json
{
  "role": "system",
  "content": "Do not show your reasoning. Answer directly."
}
```

Result: Clean response in `content` field, empty `reasoning_content`.

### Method 2: Extra Body Parameter (If Supported)
```json
{
  "model": "Qwen3-8B-Q4_K_M",
  "messages": [...],
  "extra_body": {
    "chat_template_kwargs": {
      "enable_thinking": false
    }
  }
}
```

Note: Requires server/template support. System prompt method is more reliable.

### Method 3: Template Modification (Server-side)
Modify the chat template to omit the thinking block. Requires custom template compilation.

## Qwen3 Specific Behaviors

| Behavior | Description |
|----------|-------------|
| **Reasoning default** | Always on by default |
| **Reasoning field** | `reasoning_content` (separate from `content`) |
| **Empty content** | `content` may be empty when reasoning is present |
| **Finish reason** | Often `length` when reasoning consumes tokens |

## Best Practices

1. **Always include system prompt** to disable reasoning unless you explicitly want it
2. **Set `max_tokens`** on the completion to prevent reasoning from consuming budget
3. **Use `temperature: 0.7`** for balanced creativity/consistency
4. **Check both fields** in response handling: check `reasoning_content` if `content` is empty

## Response Handling Code (JavaScript)

```javascript
function extractResponse(response) {
  const choice = response.choices[0];
  const message = choice.message;
  
  // Prefer content, fall back to reasoning_content
  const content = message.content || message.reasoning_content || '';
  
  // Clean up if reasoning leaked into content
  return content.trim();
}
```

## Temperature Recommendations

| Task | Temperature |
|------|-------------|
| Code generation | 0.2-0.4 |
| Creative writing | 0.7-0.9 |
| Analysis/reasoning | 0.5-0.7 |
| Factual QA | 0.1-0.3 |

## Context Window Notes

- Qwen3 supports up to 32k context (128k for some variants)
- 32k context with Q4_K_M 8B model → ~6.9 GB VRAM
- 16k context is safer for 8GB VRAM with headroom
- Reasoning tokens count against context limit