# Gemma 2 (offline)

Google's lightweight open models distilled from Gemini research. Weights are baked into the image at build time; the container runs with **no internet access**.

| | |
|---|---|
| **Default model id** | `google/gemma-2-2b-it` |
| **License / gating** | **Gated** — accept the license on HuggingFace and supply a token (Gemma Terms of Use) |
| **Approx. image size** | ~7 GB (CPU build) |
| **Architecture** | Causal LM (`AutoModelForCausalLM`) |

> ⚠️ **Heads up:** this is a **gated** model — you need a HuggingFace token and must accept its license. See the build step below.

## 1. Build the image locally

This model is **gated**. You must accept its license on HuggingFace and supply a
token. The token is passed as a **BuildKit secret**, so it is never baked into
the image.

```bash
# 1. Request access on the model's HuggingFace page and accept the license.
# 2. Save your token to a file (keeps it out of shell history & image layers)
printf '%s' 'hf_xxx_your_token' > "$HOME/.hf_token"

# 3. Build with the token as a BuildKit secret
DOCKER_BUILDKIT=1 docker build \
  --secret id=hf_token,src="$HOME/.hf_token" \
  -t airlock-gemma ./gemma
```

> 💡 Need a credential-free smoke test? Override the model:
> `docker build --build-arg MODEL_ID=gpt2 -t airlock-gemma ./gemma`

The build needs internet (to install dependencies and download the weights).
**Everything after the build is offline.**

## 2. Run it — fully air-gapped (recommended)

`--network none` removes networking from the container entirely, so the model
*cannot* reach the internet. Interact with it via `docker exec`:

```bash
docker run -d --name gemma --network none airlock-gemma
docker exec gemma python -c "import serve; print(serve.generate('Explain photosynthesis in one sentence.', 60))"
```

## 3. Run it — internal API, still no internet

```bash
docker network create --internal llm-net 2>/dev/null || true
docker run -d --name gemma --network llm-net -p 8000:8000 airlock-gemma

curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Explain photosynthesis in one sentence.", "max_new_tokens": 60}'
```

> ⚠️ `-p 8000:8000` only works with a network attached. With `--network none`
> there are no ports to publish — use the `docker exec` method above.

> 💡 This is an instruction-tuned model — wrap prompts in its chat format (see the model card) for best results.

## 4. Pull the pre-built image from Docker Hub

```bash
docker pull <DOCKERHUB_USERNAME>/airlock-gemma:latest
docker run -d --name gemma --network none <DOCKERHUB_USERNAME>/airlock-gemma:latest
```

> Note: gated weights may not be redistributable. Pre-built Hub images use an open fallback or require you to build locally with your token.

## Security — how internet access is blocked & why

See the [root README security section](../README.md#-security-model) for the
full rationale. Three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the library refuses to
   contact the Hub even if asked.
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.

The HuggingFace token (for gated weights) is passed as a **BuildKit secret**, so it is used only during the download step and is never persisted in an image layer or the image history.
