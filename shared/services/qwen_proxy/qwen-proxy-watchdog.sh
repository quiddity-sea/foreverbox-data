#!/usr/bin/env bash
# qwen-proxy-watchdog.sh
# Runs every 2 minutes. If the proxy on port 11435 is not responding, restarts it.
# Designed for Cron (no TTY, no rich terminal).
# Shared location: /foreverbox_data/shared/services/qwen_proxy/
# Used by: Leon, Otec, any agent needing Qwen via Ollama translation layer.

PROXY_PORT=11435
PROXY_DIR="/foreverbox_data/shared/services/qwen_proxy"
LOG_FILE="$PROXY_DIR/watchdog.log"

# Check if proxy responds
if ! curl -sf "http://localhost:$PROXY_PORT/health" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Proxy not responding on port $PROXY_PORT. Restarting..." | tee -a "$LOG_FILE"
    
    # Kill any stale process on that port
    STALE_PID=$(lsof -ti :$PROXY_PORT 2>/dev/null)
    if [ -n "$STALE_PID" ]; then
        kill "$STALE_PID" 2>/dev/null
        sleep 1
        kill -0 "$STALE_PID" 2>/dev/null && kill -9 "$STALE_PID" 2>/dev/null
    fi
    
    # Restart proxy
    cd "$PROXY_DIR" && source .venv/bin/activate && nohup python proxy.py >> "$LOG_FILE" 2>&1 &
    sleep 2
    
    if curl -sf "http://localhost:$PROXY_PORT/health" > /dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Proxy restarted successfully." | tee -a "$LOG_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Proxy restart FAILED." | tee -a "$LOG_FILE" >&2
    fi
fi