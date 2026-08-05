---
name: llama-cpp-server
category: mlops
description: Class-level skill for deploying, configuring, and managing llama.cpp inference servers with GGUF models. Covers model acquisition, server deployment, context window configuration, GPU/CPU optimization, and integration with agent profiles.
---

# llama.cpp Server Management

Class-level skill for deploying, configuring, and managing llama.cpp inference servers with GGUF models. Covers model acquisition, server deployment, context window configuration, GPU/CPU optimization, and integration with agent profiles.

## Core Concepts

### When to Use llama.cpp Server vs Ollama
- **llama.cpp server**: Lower-level control, custom context windows, OpenAI-compatible API, multi-model serving, fine-grained GPU layer control
- **Ollama**: Easier model management, automatic GPU offload, simpler CLI, built-in model library

### Model Format
- **GGUF** (GPT-Generated Unified Format) — single-file, quantized models
- Quantization levels: Q4_K_M (balanced), Q4_K_S (smaller), Q8_0 (higher quality), etc.
- Naming convention: `ModelName-Size-Quant.gguf` (e.g., `Qwen3-8B-Q4_K_M.gguf`)

## Setup & Build

### Prerequisites
```bash
sudo apt-get update && sudo apt-get install -y build-essential cmake git
```

### Build llama.cpp (CPU-only - Recommended for WSL with < 32GB RAM)
```bash
cd ~/llama.cpp
mkdir -p build && cd build
cmake .. -DGGML_CUDA=OFF
cmake --build . --target llama-server -j$(nproc)
```
**Pitfall**: If the build directory already exists but was configured for a different backend (e.g., switching from CUDA to CPU or vice versa), `cmake ..` may not override the existing cache. **Always** use `rm -rf build` first when switching backends to ensure a clean configuration.
**Pitfall (hit 2026-07-31)**: do NOT run `rm -rf build` while your shell CWD is inside `build/` (e.g. `cd ~/llama.cpp/build && rm -rf build`). The deleted CWD yields confusing follow-on failures: `getcwd() failed: No such file or directory` from the shell, and assembler errors like `Fatal error: can't create CMakeFiles/...: No such file or directory`. Always `cd` out first: `cd ~/llama.cpp && rm -rf build && mkdir build && cd build`.
**Pitfall**: a CUDA build killed mid-compile (OOM, `Ctrl+C`, timeout) leaves partial `.o`/`.d` files; resuming `make` can then fail with "missing directory" or assembler errors that look like new problems. The fix is a clean rebuild (`rm -rf build` from OUTSIDE the dir), not patching the partial tree.

### Build with CUDA (NVIDIA GPU) - Advanced
```bash
cmake .. -DGGML_CUDA=ON
cmake --build . --target llama-server -j1
```
**Requires**: CUDA Toolkit (`nvcc` in PATH) and compatible driver.
**WSL-Specific Critical Notes**: 
- CUDA compilation is extremely RAM-intensive due to nvcc memory spikes during template instantiation
- **Always use `-j1` (single-threaded)** regardless of core count to manage memory pressure
- WSL memory limits often cause silent build failures. Configure resources in `.wslconfig`:
  ```
  [wsl2]
  memory=12GB
  swap=16GB
  ```
  Then run `wsl --shutdown` in PowerShell and restart WSL for changes to take effect
- Even with increased memory, builds may still fail on systems with < 32GB total RAM
- **Decision point (hit 2026-07-31, 16GB RAM RTX-4060 WSL)**: CUDA build from source failed repeatedly with `nvcc: Terminated` at the `fattn-tile-instance` template files, even with `-j1`, 12GB WSL memory + 16GB swap, and `CMAKE_CUDA_ARCHITECTURES=89`. Also: **ggml-org/llama.cpp GitHub releases ship NO Linux CUDA binaries** — only Windows CUDA zips and Linux CPU tarballs exist, so there is no prebuilt escape hatch on WSL. Do not burn hours retrying; pivot to Ollama (see below).
- **Pivot recommendation for WSL with a GPU**: import the same GGUF into Ollama instead. Ollama ships prebuilt CUDA support, auto-detects the GPU (RTX 4060 detected as CUDA 8.9 / 8.0 GiB VRAM), and serves the model via API at `http://localhost:11434`. See `ollama-model-setup` skill for the exact modelfile procedure (ChatML template + stop tokens required to avoid thinking-token leakage/looping).
- If attempting CUDA build and encountering `nvcc: Terminated` errors, consider:
  1. Increasing virtual memory swap size
  2. Using CPU-only build as fallback
  3. Upgrading system RAM if possible
  4. Pivoting to Ollama (preferred on WSL with GPU)

### Verify Build
```bash
~/llama.cpp/build/bin/llama-server --version
```
aria2c -x 16 -s 16 -k 1M --continue=true \
  "https://huggingface.co/unsloth/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q4_K_M.gguf"
```

### Verify Download
```bash
ls -lh ~/models/Qwen3-8B-Q4_K_M.gguf
# Should be ~4.6-4.7 GB for Q4_K_M 8B model
```

## Server Deployment

### Basic CPU Server
```bash
~/llama.cpp/build/bin/llama-server \
  -m ~/models/Qwen3-8B-Q4_K_M.gguf \
  -c 32768 \                    # Context window (32k)
  --host 0.0.0.0 \              # Listen on all interfaces
  --port 11436 \                # Port (avoid 11434 = Ollama)
  --threads $(nproc)            # Use all CPU threads
```

### GPU Offload (if CUDA build)
```bash
~/llama.cpp/build/bin/llama-server \
  -m ~/models/Qwen3-8B-Q4_K_M.gguf \
  -c 32768 \
  -ngl 99 \                     # Offload all layers to GPU
  --host 0.0.0.0 --port 11436
```

### Key Flags
| Flag | Purpose |
|------|---------|
| `-m` | Model path |
| `-c` | Context window (tokens) |
| `-ngl` | GPU layers to offload (99 = all) |
| `--host` | Bind address (0.0.0.0 = all interfaces) |
| `--port` | Listen port |
| `--threads` | CPU threads |
| `--ctx-size` | Alias for `-c` |
| `--mlock` | Lock model in RAM (prevents swap) |
| `--no-mmap` | Disable mmap (use with `--mlock`) |

## Context Window Configuration

### VRAM Requirements (Approximate)
| Model Size | Quant | 4k ctx | 16k ctx | 32k ctx | 64k ctx |
|------------|-------|--------|---------|---------|---------|
| 7B Q4_K_M | ~4.7 GB | 5.2 GB | 6.0 GB | 6.8 GB | 8.4 GB |
| 8B Q4_K_M | ~4.7 GB | 5.3 GB | 6.1 GB | 6.9 GB | 8.5 GB |

**Rule of thumb**: Base model + (context_tokens × 2 bytes per token) + overhead

### 8 GB VRAM Limits
- Qwen3-8B-Q4_K_M at 32k ctx → ~6.9 GB (fits with headroom)
- Two 8B models at 32k → **OOM** (needs ~14 GB)
- **Solution**: Run one model on GPU, one on CPU; or use smaller context

## API Usage

### Health Check
```bash
curl http://localhost:11436/health
```

### Chat Completion (OpenAI-compatible)
```bash
curl -X POST http://localhost:11436/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3-8B-Q4_K_M",
    "messages": [
      {"role": "system", "content": "Do not show your reasoning. Answer directly."},
      {"role": "user", "content": "Say hello in one sentence"}
    ],
    "max_tokens": 30,
    "temperature": 0.7
  }'
```

### Disable Reasoning (Qwen3)
Qwen3 models output reasoning in `reasoning_content` by default. Suppress with system prompt:
```json
{"role": "system", "content": "Do not show your reasoning. Answer directly."}
```

Or use `extra_body.chat_template_kwargs.enable_thinking: false` (if supported).

## Agent Profile Integration

### Hermes Profile Config (`~/.hermes/profiles/agent/config.yaml`)
```yaml
custom_providers:
  - name: qwen-local
    base_url: http://localhost:11436/v1
    model: Qwen3-8B-Q4_K_M
    # context_length: 32768  # optional override
```

### Use in Profile
```yaml
model: qwen-local
provider: custom
```

## Monitoring & Debugging

### Health Check
```bash
curl http://localhost:11436/health
```

### Model Info
```bash
curl http://localhost:11436/v1/models
```

### GPU Usage
```bash
watch -n 1 nvidia-smi
```

### Logs
```bash
# If running in background with systemd
journalctl -u llama-server -f

# If running directly, check terminal output
```

## Common Issues & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `CUDA Toolkit not found` | Missing CUDA Toolkit in WSL | Install CUDA Toolkit via official NVIDIA guides for WSL (not just Windows drivers). Verify with `nvcc --version` before building. |
| `couldn't bind HTTP server socket` | Port conflict | Use a different port (e.g., `--port 8081`) or kill the process occupying the port using `fuser -k <port>/tcp`. |
| `403 Forbidden` on download | HF rate limit | Add token: `-H "Authorization: Bearer $HF_TOKEN"` |
| Model won't load (OOM) | VRAM exhausted | Reduce `-c` (context), reduce `-ngl`, or use CPU |
| `503 Loading model` | Model still loading | Wait 30-60s for 4.6 GB model on CPU |
| Slow generation | CPU-only | Enable GPU with `-ngl 99` (requires CUDA build) |
| Reasoning output in response | Qwen3 default | Add system prompt: "Do not show your reasoning" |

## Maintenance

## llama.cpp with CUDA

Common issues and solutions

### Update llama.cpp
```bash
cd ~/llama.cpp
git pull
cd build && cmake .. -DGGML_CUDA=OFF && cmake --build . --target llama-server -j$(nproc)
```

### Update Model
```bash
cd ~/models
aria2c -x 16 -s 16 -k 1M --continue=true "https://huggingface.co/.../resolve/main/NewModel.gguf"
# Restart server to load new model
```

### Backup Models
```bash
rsync -av ~/models/ /backup/models/
```

## Troubleshooting

Common issues and solutions when building and running llama.cpp with CUDA:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `CUDA Toolkit not found` | Missing CUDA Toolkit in WSL | Install CUDA Toolkit via official NVIDIA guides for WSL (not just Windows drivers). Verify with `nvcc --version` before building. |
| `couldn't bind HTTP server socket` | Port conflict | Use a different port (e.g., `--port 8081`) or kill the process occupying the port using `fuser -k <port>/tcp`. |
| `403 Forbidden` on download | HF rate limit | Add token: `-H "Authorization: Bearer $HF_TOKEN"` |
| Model won't load (OOM) | VRAM exhausted | Reduce `-c` (context), reduce `-ngl`, or use CPU |
| `503 Loading model` | Model still loading | Wait 30-60s for 4.6 GB model on CPU |
| Slow generation | CPU-only | Enable GPU with `-ngl 99` (requires CUDA build) |
| Reasoning output in response | Qwen3 default | Add system prompt: "Do not show your reasoning" |
| `nvcc: Terminated` during build | WSL memory exhaustion during CUDA compilation | Use `-j1` flag, increase WSL memory/swap in `.wslconfig` (e.g., `memory=12GB`, `swap=16GB`), then run `wsl --shutdown` in PowerShell and restart WSL. Consider CPU-only build if issues persist. |
| Build fails with missing files/directories | Incomplete build directory or interrupted compilation | Remove build directory (`rm -rf build`) and start fresh with `cmake .. -DGGML_CUDA=ON` followed by `make -j1 llama-server` |

## Related Skills
- `local-model-ollama-context` — Ollama model management
- `fbox-wolf-spawn` — Spawning research workers (may use local models)
- `hermes-agent` — Profile configuration for custom providers

## References
- `references/llama_cpp_build.md` — Detailed build options
- `references/gguf_quantization.md` — Quantization comparison
- `references/vram_calculation.md` — VRAM estimation formulas
- `references/qwen3_prompting.md` — Qwen3 prompting best practices

## Troubleshooting

Common issues and solutions when building and running llama.cpp with CUDA:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `CUDA Toolkit not found` | Missing CUDA Toolkit in WSL | Install CUDA Toolkit via official NVIDIA guides for WSL (not just Windows drivers). Verify with `nvcc --version` before building. |
| `couldn't bind HTTP server socket` | Port conflict | Use a different port (e.g., `--port 8081`) or kill the process occupying the port using `fuser -k <port>/tcp`. |
| `403 Forbidden` on download | HF rate limit | Add token: `-H "Authorization: Bearer $HF_TOKEN"` |
| Model won't load (OOM) | VRAM exhausted | Reduce `-c` (context), reduce `-ngl`, or use CPU |
| `503 Loading model` | Model still loading | Wait 30-60s for 4.6 GB model on CPU |
| Slow generation | CPU-only | Enable GPU with `-ngl 99` (requires CUDA build) |
| Reasoning output in response | Qwen3 default | Add system prompt: "Do not show your reasoning" |
| `nvcc: Terminated` during build | WSL memory exhaustion during CUDA compilation | Use `-j1` flag, increase WSL memory/swap in `.wslconfig` (e.g., `memory=12GB`, `swap=16GB`), then run `wsl --shutdown` in PowerShell and restart WSL. Consider CPU-only build if issues persist. |
| Build fails with missing files/directories | Incomplete build directory or interrupted compilation | Remove build directory (`rm -rf build`) and start fresh with `cmake .. -DGGML_CUDA=ON` followed by `make -j1 llama-server` |

## Related Skills
- `local-model-ollama-context` — Ollama model management
- `fbox-wolf-spawn` — Spawning research workers (may use local models)
- `hermes-agent` — Profile configuration for custom providers

## References
- `references/llama_cpp_build.md` — Detailed build options
- `references/gguf_quantization.md` — Quantization comparison
- `references/vram_calculation.md` — VRAM estimation formulas
- `references/qwen3_prompting.md` — Qwen3 prompting best practices