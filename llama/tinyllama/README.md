<div align="center">

# 🦙 Llama · offline

A self-contained, **network-isolated** container that serves a Llama-family chat
model for local text generation. Weights are baked into the image at build time;
the container runs with **no internet access**.

![Weights](https://img.shields.io/badge/weights-open_default-2f9e44?style=flat-square)
![Image](https://img.shields.io/badge/image-~4_GB-2496ED?style=flat-square&logo=docker&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-air--gapped-862e9c?style=flat-square)
![Transformers](https://img.shields.io/badge/Hugging%20Face-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

</div>

---

| | |
|---|---|
| 🆔 **Default model id** | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (open) |
| 📜 **License / gating** | Default is open. Meta's official Llama weights are **gated** (token required). |
| 💾 **Approx. image size** | ~4 GB (TinyLlama, CPU build) |
| 🏗️ **Architecture** | Causal LM (`AutoModelForCausalLM`) |

> [!NOTE]
> The default is the open **TinyLlama** chat model so this image builds with no
> credentials. To run Meta's official Llama, see *Using gated Meta weights*
> below.

## 🔨 1 · Build the image locally

```bash
# from the repository root -- open default, no token needed
docker build -t airlock-tinyllama ./llama/tinyllama
```

### 🔑 Using gated Meta weights

Meta's Llama weights require accepting the license on HuggingFace and a token.

```bash
# 1. Request access: https://huggingface.co/meta-llama
# 2. Put your token in a file (keeps it out of shell history & image layers)
printf '%s' 'hf_xxx_your_token' > "$HOME/.hf_token"

# 3. Build with the token as a BuildKit secret (never baked into the image)
DOCKER_BUILDKIT=1 docker build \
  --build-arg MODEL_ID=meta-llama/Llama-2-7b-chat-hf \
  --secret id=hf_token,src="$HOME/.hf_token" \
  -t airlock-tinyllama ./llama/tinyllama
```

> [!WARNING]
> 7B weights are ~13–15 GB. Ensure you have the disk/RAM for it.

The build needs internet (to install dependencies and download the weights).
**Everything after the build is offline.**

## 🚀 2 · Run — fully air-gapped (recommended)

```bash
docker run -d --name llama --network none airlock-tinyllama
docker exec llama python -c "import serve; print(serve.generate('Explain gravity simply.', 80))"
```

## 🌐 3 · Run — internal API, still no internet

```bash
docker network create --internal llm-net
docker run -d --name llama --network llm-net -p 8000:8000 airlock-tinyllama

curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Explain gravity simply.", "max_new_tokens": 80}'
```

> [!IMPORTANT]
> `-p 8000:8000` only works with a network attached. With `--network none` there
> are no ports to publish — use the `docker exec` method above.

## ⬇️ 4 · Pull the pre-built image from ghcr.io

```bash
docker pull ghcr.io/dante0747/airlock-tinyllama:latest
docker run -d --name llama --network none ghcr.io/dante0747/airlock-tinyllama:latest
```

> [!CAUTION]
> Pre-built images in the registry use the **open** default model. Gated Meta
> weights cannot be redistributed — build those locally with your token.

## 🔐 Security — how internet access is blocked & why

See the [root README security section](../../README.md#-security-model) for the
full rationale. Three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the library refuses to
   contact the Hub even if asked.
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.

> [!NOTE]
> The HuggingFace token (for gated weights) is passed as a **BuildKit secret**,
> so it is used only during the download step and is never persisted in an image
> layer or the image history.
