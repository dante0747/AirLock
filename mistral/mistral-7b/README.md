<div align="center">

# 🌬️ Mistral · offline

A self-contained, **network-isolated** container that serves Mistral's
instruction-tuned model for local text generation. Weights are baked into the
image at build time; the container runs with **no internet access**.

![Weights](https://img.shields.io/badge/weights-gated-e8590c?style=flat-square)
![Image](https://img.shields.io/badge/image-~16_GB-2496ED?style=flat-square&logo=docker&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-air--gapped-862e9c?style=flat-square)
![Transformers](https://img.shields.io/badge/Hugging%20Face-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

</div>

---

| | |
|---|---|
| 🆔 **Default model id** | `mistralai/Mistral-7B-Instruct-v0.2` |
| 📜 **License / gating** | **Gated** — accept the license on HuggingFace and supply a token |
| 💾 **Approx. image size** | ~16 GB (7B, CPU build) |
| 🏗️ **Architecture** | Causal LM (`AutoModelForCausalLM`) |

> [!WARNING]
> **Heads up:** the default is a **gated, ~14 GB** model. You need a HuggingFace
> token *and* a machine with enough disk/RAM. For a quick, credential-free smoke
> test, override `MODEL_ID` with an open model (see below).

## 🔨 1 · Build the image locally

```bash
# 1. Request access: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
# 2. Save your token to a file (keeps it out of shell history & image layers)
printf '%s' 'hf_xxx_your_token' > "$HOME/.hf_token"

# 3. Build with the token as a BuildKit secret (never baked into the image)
DOCKER_BUILDKIT=1 docker build \
  --secret id=hf_token,src="$HOME/.hf_token" \
  -t airlock-mistral-7b ./mistral/mistral-7b
```

### 🧪 Credential-free smoke test (open model)

```bash
docker build \
  --build-arg MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  -t airlock-mistral-7b ./mistral/mistral-7b
```

The build needs internet (to install dependencies and download the weights).
**Everything after the build is offline.**

## 🚀 2 · Run — fully air-gapped (recommended)

```bash
docker run -d --name mistral --network none airlock-mistral-7b
docker exec mistral python -c "import serve; print(serve.generate('[INST] Summarize the water cycle. [/INST]', 120))"
```

## 🌐 3 · Run — internal API, still no internet

```bash
docker network create --internal llm-net
docker run -d --name mistral --network llm-net -p 8000:8000 airlock-mistral-7b

curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "[INST] Summarize the water cycle. [/INST]", "max_new_tokens": 120}'
```

> [!IMPORTANT]
> `-p 8000:8000` only works with a network attached. With `--network none` there
> are no ports to publish — use the `docker exec` method above.

> [!TIP]
> Mistral-Instruct expects the `[INST] ... [/INST]` prompt format shown above.

## ⬇️ 4 · Pull the pre-built image from ghcr.io

```bash
docker pull ghcr.io/dante0747/airlock-mistral-7b:latest
docker run -d --name mistral --network none ghcr.io/dante0747/airlock-mistral-7b:latest
```

> [!CAUTION]
> Mistral's license may restrict redistribution of weights. If you publish a
> pre-built image, confirm you are permitted to, or publish only the open
> smoke-test variant. See [`/docker-images`](../../docker-images/README.md).

## 🔐 Security — how internet access is blocked & why

See the [root README security section](../../README.md#-security-model) for the
full rationale. Three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the library refuses to
   contact the Hub even if asked.
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.

> [!NOTE]
> The HuggingFace token is passed as a **BuildKit secret**, so it is used only
> during the download step and is never persisted in an image layer or history.
