<div align="center">

# ♾️ MiniMax-M3 · offline

MiniMax AI's M-series is a **Mixture-of-Experts reasoning model** with open
(Apache-2.0) weights. Weights are baked into the image at build time; the
container runs with **no internet access**.

![Weights](https://img.shields.io/badge/weights-open_(Apache--2.0)-2f9e44?style=flat-square)
![Image](https://img.shields.io/badge/image-large_(MoE)-2496ED?style=flat-square&logo=docker&logoColor=white)
![Runtime](https://img.shields.io/badge/runtime-air--gapped-862e9c?style=flat-square)
![Transformers](https://img.shields.io/badge/Hugging%20Face-Transformers_%E2%89%A5_4.48-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

</div>

---

| | |
|---|---|
| 🆔 **Default model id** | `MiniMaxAI/MiniMax-M3` |
| 📜 **License / gating** | Apache-2.0 — open, no token required |
| 💾 **Approx. image size** | Large — this is a Mixture-of-Experts model |
| 🏗️ **Architecture** | Causal LM, MoE (`AutoModelForCausalLM`, `trust_remote_code`) |

> [!NOTE]
> MiniMax-M3 ships a **custom MoE architecture**, so `serve.py` loads it with
> `trust_remote_code=True`. That code is baked into the image at build time, so
> the runtime stays fully offline — `HF_HUB_OFFLINE=1` makes transformers run
> the cached modeling code without ever touching the network.

> [!IMPORTANT]
> This is a **large** model. Baking the full weights produces a correspondingly
> large image that may exceed a CI runner's disk. For a quick credential-free
> smoke test, override `MODEL_ID` with a small model:
> `docker build --build-arg MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct -t airlock-minimax-m3 ./minimax/minimax-m3`

## 🔨 1 · Build the image locally

```bash
# from the repository root — no credentials required
docker build -t airlock-minimax-m3 ./minimax/minimax-m3
```

The build needs internet (to install dependencies and download the weights).
**Everything after the build is offline.**

## 🚀 2 · Run — fully air-gapped (recommended)

`--network none` removes networking from the container entirely, so the model
*cannot* reach the internet. Interact with it via `docker exec`:

```bash
docker run -d --name minimax --network none airlock-minimax-m3
docker exec minimax python -c "import serve; print(serve.generate('What is the capital of France?', 60))"
```

## 🌐 3 · Run — internal API, still no internet

```bash
docker network create --internal llm-net 2>/dev/null || true
docker run -d --name minimax --network llm-net -p 8000:8000 airlock-minimax-m3

curl -s localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "What is the capital of France?", "max_new_tokens": 60}'
```

> [!IMPORTANT]
> `-p 8000:8000` only works with a network attached. With `--network none` there
> are no ports to publish — use the `docker exec` method above.

> [!TIP]
> This is an instruction-tuned reasoning model — wrap prompts in its chat format
> (see the model card) for best results.

## ⬇️ 4 · Pull the pre-built image from ghcr.io

```bash
docker pull ghcr.io/dante0747/airlock-minimax-m3:latest
docker run -d --name minimax --network none ghcr.io/dante0747/airlock-minimax-m3:latest
```

## 🔐 Security — how internet access is blocked & why

See the [root README security section](../../README.md#-security-model) for the
full rationale. Three independent layers keep this model offline:

1. **Weights baked at build time** → nothing to download at runtime.
2. **`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`** → the library refuses to
   contact the Hub even if asked (this also makes `trust_remote_code` run the
   cached modeling code rather than fetching it).
3. **`docker run --network none`** → the kernel gives the container no network
   interface at all.
