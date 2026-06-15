# BLOOM (offline)

BigScience's massively multilingual open language model. Weights are baked into the image at build time; the container runs with **no internet access**.

| | |
|---|---|
| **Default model id** | `bigscience/bloom-560m` |
| **License / gating** | BigScience RAIL — open, no token required |
| **Approx. image size** | ~2.5 GB (CPU build) |
| **Architecture** | Causal LM (`AutoModelForCausalLM`) |

## 1. Build the image locally

```bash
# from the repository root — no credentials required
docker build -t airlock-bloom ./bloom
```

The build needs internet (to install dependencies and download the weights).
**Everything after the build is offline.**

## 2. Run it — fully air-gapped (recommended)

`--network none` removes networking from the container entirely, so the model
*cannot* reach the internet. Interact with it via `docker exec`:

```bash
docker run -d --name bloom --network none airlock-bloom
docker exec bloom python -c "import serve; print(serve.generate('Once upon a time', 60))"
```

## 3. Run it — internal API, still no internet

```bash
docker network create --internal llm-net 2>/dev/null || true
docker run -d --name bloom --network llm-net -p 8000:8000 airlock-bloom

curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Once upon a time", "max_new_tokens": 60}'
```

> ⚠️ `-p 8000:8000` only works with a network attached. With `--network none`
> there are no ports to publish — use the `docker exec` method above.

> 💡 This is a base completion model — it continues your text rather than following instructions.

## 4. Pull the pre-built image from Docker Hub

```bash
docker pull <DOCKERHUB_USERNAME>/airlock-bloom:latest
docker run -d --name bloom --network none <DOCKERHUB_USERNAME>/airlock-bloom:latest
```

## Security — how internet access is blocked & why

See the [root README security section](../README.md#-security-model) for the
full rationale. Three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the library refuses to
   contact the Hub even if asked.
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.
