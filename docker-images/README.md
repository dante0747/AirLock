<div align="center">

# 📦 Pre-built images

### The `ghcr.io` catalog for Airlock

**Every model, built automatically on every push to `main` and on a daily schedule.**

[![Registry](https://img.shields.io/badge/registry-ghcr.io-2496ED?style=flat-square&logo=docker&logoColor=white)](#%EF%B8%8F-image-catalog)
[![Tags](https://img.shields.io/badge/tags-latest_·_date_·_sha-862e9c?style=flat-square)](#%EF%B8%8F-tagging-scheme)

</div>

---

This directory documents the pre-built **Airlock** images published to the
GitHub Container Registry (`ghcr.io`) by the
[CI/CD workflow](../.github/workflows/docker-build.yml).

> [!NOTE]
> **Why a directory and not a branch?** Keeping the catalog as docs alongside
> the Dockerfiles means it versions together with the code that produces the
> images. If you prefer a branch strategy instead, a common convention is a
> `docker-images` orphan branch holding only published manifests/notes — but the
> directory approach below is the default for this template.

## 🗂️ Image catalog

Every image is published under the repo owner as `ghcr.io/dante0747/<image>`.

> [!IMPORTANT]
> Replace `dante0747` with your **lowercased** GitHub owner (ghcr.io requires the
> path to be lowercase).

| Model | Image | Gated? | Notes |
|-------|-------|:------:|-------|
| 🤖 GPT-2 | `airlock-gpt2` | — | Open weights, builds with no credentials (reference model) |
| 🦙 Llama | `airlock-llama` | — | Published image uses the open TinyLlama default |
| 🌬️ Mistral | `airlock-mistral` | 🔑 | Gated weights — see licensing note below |
| 💎 Gemma 2 | `airlock-gemma` | 🔑 | Needs `HF_TOKEN`; gated by Google |
| 🔬 Phi-2 | `airlock-phi` | — | MIT licensed |
| 🌏 Qwen2.5 | `airlock-qwen` | — | Apache-2.0 |
| 🦅 Falcon3 | `airlock-falcon` | — | TII Falcon License |
| 🌸 BLOOM | `airlock-bloom` | — | BigScience RAIL license |
| 🔮 Pythia | `airlock-pythia` | — | Apache-2.0 |
| ⚖️ StableLM 2 | `airlock-stablelm` | 🔑 | Needs `HF_TOKEN`; gated by Stability AI |
| 📂 OPT | `airlock-opt` | — | Non-commercial license |
| 🧬 GPT-Neo | `airlock-gptneo` | — | MIT licensed |
| 💻 DeepSeek Coder | `airlock-deepseek` | — | Code-specialized |
| 🤏 SmolLM2 | `airlock-smollm` | — | Apache-2.0, tiny |
| 🍃 Zephyr | `airlock-zephyr` | — | MIT; ~16 GB image |
| 🔭 OLMo 2 | `airlock-olmo` | — | Apache-2.0; fully open (weights + training data) |
| ⚡ GLM-Edge | `airlock-glm` | — | GLM-4 license; Z.ai on-device model |

All images share the same tags: `latest`, `YYYYMMDD`, and `<git-sha>`.

### 📍 Full image paths

Every image lives at `ghcr.io/dante0747/airlock-<model>`. The complete list
(swap in your **lowercased** owner):

```text
ghcr.io/dante0747/airlock-gpt2
ghcr.io/dante0747/airlock-llama
ghcr.io/dante0747/airlock-mistral
ghcr.io/dante0747/airlock-gemma
ghcr.io/dante0747/airlock-phi
ghcr.io/dante0747/airlock-qwen
ghcr.io/dante0747/airlock-falcon
ghcr.io/dante0747/airlock-bloom
ghcr.io/dante0747/airlock-pythia
ghcr.io/dante0747/airlock-stablelm
ghcr.io/dante0747/airlock-opt
ghcr.io/dante0747/airlock-gptneo
ghcr.io/dante0747/airlock-deepseek
ghcr.io/dante0747/airlock-smollm
ghcr.io/dante0747/airlock-zephyr
ghcr.io/dante0747/airlock-olmo
ghcr.io/dante0747/airlock-glm
```

> [!TIP]
> Append a tag to pin a build — e.g. `ghcr.io/dante0747/airlock-gpt2:latest`,
> `:20260616` (daily), or `:<git-sha>` (exact commit).

## 🏷️ Tagging scheme

Every successful CI run pushes three tags per model:

| Tag | Example | Meaning |
|-----|---------|---------|
| `latest` | `airlock-gpt2:latest` | Most recent successful build |
| `YYYYMMDD` | `airlock-gpt2:20260616` | Daily snapshot (immutable point-in-time) |
| `<git-sha>` | `airlock-gpt2:9f2c1ab...` | Exact commit the image was built from |

## ⬇️ Pulling and running

```bash
docker pull ghcr.io/dante0747/airlock-gpt2:latest

# Run fully air-gapped (no network interface in the container)
docker run -d --name gpt2 --network none ghcr.io/dante0747/airlock-gpt2:latest
docker exec gpt2 python -c "import serve; print(serve.generate('Hello', 32))"
```

Pin to a dated or sha tag for reproducibility:

```bash
docker pull ghcr.io/dante0747/airlock-gpt2:20260616
```

> [!NOTE]
> **Private by default.** New ghcr.io packages start private — to pull one before
> you make it public, authenticate first with a token that has the
> `read:packages` scope:
>
> ```bash
> echo "$GHCR_PAT" | docker login ghcr.io -u dante0747 --password-stdin
> ```
>
> Or set the package to **Public** (repo → Packages → the image → Package
> settings) to pull without any login.

## ⚖️ Licensing / redistribution note

Pre-built images bundle model weights, which carry their **own** licenses:

- ✅ **Open** (GPT-2, TinyLlama, Phi-2, Qwen2.5, Falcon3, BLOOM, Pythia, OPT,
  GPT-Neo, DeepSeek, SmolLM2, Zephyr) — generally safe to redistribute, but check
  each model's specific terms (some, like OPT, are research/non-commercial).
- 🔑 **Gated** (Mistral, Gemma, StableLM, official Meta Llama) — may **restrict
  redistribution**.

> [!CAUTION]
> If you publish gated images, confirm you are permitted to — otherwise publish
> only an open fallback, or have users build locally with their own HuggingFace
> token.

## 🔄 How publishing works

1. CI logs in to `ghcr.io` using the built-in `GITHUB_TOKEN` (no personal
   secrets needed).
2. Each model in the build matrix is built from its `Dockerfile`.
3. Images are tagged (`latest` / date / sha) and pushed.
4. Pull requests build the images **but do not push** them.

See the [root README CI/CD section](../README.md#%EF%B8%8F-cicd) for trigger and
secret details.
