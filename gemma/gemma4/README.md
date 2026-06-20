<div align="center">

# 💠 Gemma 4 12B · offline

Google's Gemma 4 — a unified, encoder-free **multimodal** open model — in a
self-contained **network-isolated** container. Served from a **4-bit GGUF via
llama.cpp** (the same quantization Ollama's `gemma4:12b` ships), so the image is
~8 GB and CPU-friendly. Weights are baked in at build time; the container runs
with **no internet access**.

![Weights](https://img.shields.io/badge/weights-open_(Apache--2.0)-2f9e44?style=flat-square)
![Image](https://img.shields.io/badge/image-~8_GB-2496ED?style=flat-square&logo=docker&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-air--gapped-862e9c?style=flat-square)
![llama.cpp](https://img.shields.io/badge/runtime-llama.cpp-ff6f00?style=flat-square)

</div>

---

| | |
|---|---|
| 🆔 **Default model** | `unsloth/gemma-4-12b-it-GGUF` · `gemma-4-12b-it-Q4_K_M.gguf` |
| 📜 **License / gating** | Apache-2.0 — **open**, no token required |
| 💾 **Approx. image size** | ~8 GB (CPU build) — the Q4_K_M weights are ~7.6 GB |
| 🏗️ **Runtime** | `llama.cpp` (`llama-cpp-python`), text-in / text-out |

> [!NOTE]
> **Why GGUF here and not transformers?** The other models bake full-precision
> safetensors and load them with `transformers`. A 12B model that way is ~24 GB
> of weights (a ~28 GB image). Serving the **4-bit GGUF via llama.cpp** instead
> keeps it to ~8 GB and runs far better on CPU — at a small quality cost. Unlike
> the gated [Gemma 2](../gemma2/README.md) image, Gemma 4 is **Apache-2.0 and not
> gated**, so no HuggingFace token is needed.

> [!TIP]
> Want higher fidelity? Build a different quant with
> `--build-arg MODEL_FILE=gemma-4-12b-it-Q8_0.gguf` (~13 GB, near-lossless), or
> point at another GGUF repo with `--build-arg MODEL_ID=...`.

## 🔨 1 · Build the image locally

```bash
# from the repository root — no credentials required
docker build -t airlock-gemma4 ./gemma/gemma4
```

The build needs internet (to install dependencies and download the GGUF).
**Everything after the build is offline.**

## 🚀 2 · Run — fully air-gapped (recommended)

`--network none` removes networking from the container entirely, so the model
*cannot* reach the internet. Interact with it via `docker exec`:

```bash
docker run -d --name gemma4 --network none airlock-gemma4
docker exec gemma4 python -c "import serve; print(serve.generate('Explain photosynthesis in one sentence.', 60))"
```

## 🌐 3 · Run — internal API, still no internet

```bash
docker network create --internal llm-net 2>/dev/null || true
docker run -d --name gemma4 --network llm-net -p 8000:8000 airlock-gemma4

curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Explain photosynthesis in one sentence.", "max_new_tokens": 60}'
```

> [!IMPORTANT]
> `-p 8000:8000` only works with a network attached. With `--network none` there
> are no ports to publish — use the `docker exec` method above.

> [!TIP]
> `serve.py` uses llama.cpp's chat completion, which applies the chat template
> embedded in the GGUF — just send the raw instruction as the prompt.

## ⬇️ 4 · Pull the pre-built image from ghcr.io

```bash
docker pull ghcr.io/dante0747/airlock-gemma4:latest
docker run -d --name gemma4 --network none ghcr.io/dante0747/airlock-gemma4:latest
```

## 🔐 Security — how internet access is blocked & why

See the [root README security section](../../README.md#-security-model) for the
full rationale. Three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the HuggingFace stack
   refuses to contact the Hub even if asked (and the model loads from a local
   file path, so it never tries).
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.
