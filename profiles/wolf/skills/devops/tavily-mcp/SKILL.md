---
name: tavily-mcp
description: "Tavily MCP server for high-performance AI research and web search."
---

# Tavily MCP Setup

To integrate the Tavily MCP server into your Hermes Agent:

1. Add the configuration to your Hermes Agent setup (typically `~/.hermes/config.yaml` or equivalent).
2. Ensure you have the `mcp-server-tavily` package or the server binary installed.

## Configuration Template

Add this to your MCP configuration block:

```yaml
mcpServers:
  tavily:
    command: "npx"
    args: ["-y", "@tavily/mcp-server"]
    env:
      TAVILY_API_KEY: "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"
```

## Verification

After updating your configuration and restarting the Hermes session, verify the connection:

```bash
# Example check command (varies by system/agent implementation)
hermes mcp list
```

Ensure the Tavily server appears as "connected" or "ready."
