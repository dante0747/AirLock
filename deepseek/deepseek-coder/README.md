<div align="center">

# 💻 DeepSeek Coder · offline

DeepSeek's code-specialized model trained on 2T tokens, in a self-contained
**network-isolated** container. Weights are baked into the image at build time;
the container runs with **no internet access**.

![Weights](https://img.shields.io/badge/weights-open-2f9e44?style=flat-square)
![Image](https://img.shields.io/badge/image-~4_GB-2496ED?style=flat-square&logo=docker&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-air--gapped-862e9c?style=flat-square)
![Transformers](https://img.shields.io/badge/Hugging%20Face-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

</div>

---

| | |
|---|---|
| 🆔 **Default model id** | `deepseek-ai/deepseek-coder-1.3b-instruct` |
| 📜 **License / gating** | DeepSeek License — open, no token required |
| 💾 **Approx. image size** | ~4 GB (CPU build) |
| 🏗️ **Architecture** | Causal LM (`AutoModelForCausalLM`) |

## 🔨 1 · Build the image locally

```bash
# from the repository root — no credentials required
docker build -t airlock-deepseek-coder ./deepseek/deepseek-coder
```

The build needs internet (to install dependencies and download the weights).
**Everything after the build is offline.**

## 🚀 2 · Run — fully air-gapped (recommended)

`--network none` removes networking from the container entirely, so the model
*cannot* reach the internet. Interact with it via `docker exec`:

```bash
docker run -d --name deepseek --network none airlock-deepseek-coder
docker exec deepseek python -c "import serve; print(serve.generate('# Write a Python function to reverse a string\n', 60))"
```

## 🌐 3 · Run — internal API, still no internet

```bash
docker network create --internal llm-net 2>/dev/null || true
docker run -d --name deepseek --network llm-net -p 8000:8000 airlock-deepseek-coder

curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "# Write a Python function to reverse a string\n", "max_new_tokens": 60}'
```

> [!IMPORTANT]
> `-p 8000:8000` only works with a network attached. With `--network none` there
> are no ports to publish — use the `docker exec` method above.

> [!TIP]
> This is a code model — prompt it with a comment or function signature.

## ⬇️ 4 · Pull the pre-built image from ghcr.io

```bash
docker pull ghcr.io/dante0747/airlock-deepseek-coder:latest
docker run -d --name deepseek --network none ghcr.io/dante0747/airlock-deepseek-coder:latest
```

## 🔐 Security — how internet access is blocked & why

See the [root README security section](../../README.md#-security-model) for the
full rationale. Three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the library refuses to
   contact the Hub even if asked.
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.
