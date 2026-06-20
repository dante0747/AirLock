<div align="center">

# 🤖 GPT-2 · offline

OpenAI's [GPT-2](https://huggingface.co/gpt2) for local text generation, in a
self-contained **network-isolated** container. Weights are baked into the image
at build time; the container runs with **no internet access**.

![Weights](https://img.shields.io/badge/weights-open-2f9e44?style=flat-square)
![Image](https://img.shields.io/badge/image-~2.5_GB-2496ED?style=flat-square&logo=docker&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-air--gapped-862e9c?style=flat-square)
![Transformers](https://img.shields.io/badge/Hugging%20Face-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

</div>

---

| | |
|---|---|
| 🆔 **Default model id** | `gpt2` (124M params) |
| 📜 **License / gating** | Open, no token required |
| 💾 **Approx. image size** | ~2.5 GB (CPU build) |
| 🏗️ **Architecture** | Causal LM (`AutoModelForCausalLM`) |

> [!TIP]
> This is the **reference model** for the repo — it builds and runs with zero
> credentials, so use it to validate your setup before moving on to the larger
> gated models.

## 🔨 1 · Build the image locally

```bash
# from the repository root
docker build -t airlock-gpt2 ./gpt2

# (optional) pick a different GPT-2 variant
docker build --build-arg MODEL_ID=distilgpt2 -t airlock-gpt2 ./gpt2
```

The build needs internet (to install dependencies and download the weights).
**Everything after the build is offline.**

## 🚀 2 · Run — fully air-gapped (recommended)

`--network none` removes networking from the container entirely, so the model
*cannot* reach the internet. Interact with it via `docker exec`:

```bash
docker run -d --name gpt2 --network none airlock-gpt2

# generate from inside the container (no network needed)
docker exec gpt2 python -c "import serve; print(serve.generate('Hello, world.', 40))"
```

## 🌐 3 · Run — internal API, still no internet

If you want the HTTP API, attach the container to a Docker **internal** network.
`--internal` blocks all outbound traffic while still allowing local clients on
the same network:

```bash
docker network create --internal llm-net
docker run -d --name gpt2 --network llm-net -p 8000:8000 airlock-gpt2

curl -s localhost:8000/health
curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "The future of AI is", "max_new_tokens": 40}'
```

> [!IMPORTANT]
> `-p 8000:8000` only works with a network attached. With `--network none` there
> are no ports to publish — use the `docker exec` method above.

## ⬇️ 4 · Pull the pre-built image from ghcr.io

```bash
docker pull ghcr.io/dante0747/airlock-gpt2:latest
docker run -d --name gpt2 --network none ghcr.io/dante0747/airlock-gpt2:latest
```

Available tags: `latest`, `YYYYMMDD` (daily), and `<git-sha>`. See
[`/docker-images`](../docker-images/README.md) for the full catalog.

## 🔐 Security — how internet access is blocked & why

See the [root README security section](../README.md#-security-model) for the
full rationale. In short, three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the library refuses to
   contact the Hub even if asked.
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.

> [!IMPORTANT]
> **Why:** local LLM weights and the prompts you feed them are sensitive. An
> air-gapped container guarantees prompts/outputs can't be exfiltrated and that a
> compromised dependency can't call home.
