# Contributing

Thanks for helping grow this collection of offline LLM images! There are two
common contributions: **adding a new model** and **improving an existing one**.

## Ground rules

- **Isolation is non-negotiable.** Every image must run with **no internet
  access** at runtime. Weights are baked in at build time; the runtime is
  air-gapped. A PR that requires network access at runtime will not be merged.
- **Keep secrets out of images.** Tokens for gated models must be passed as
  **BuildKit secrets** (`--mount=type=secret`), never via `ENV` or `ARG`.
- **Prefer an open default.** If a model is gated, set the directory's default
  `MODEL_ID` to an open weight where possible, and document the gated upgrade
  path. This keeps CI green without secrets.

## Adding a new model

1. **Create a directory** named after the model (lowercase, no spaces), e.g.
   `phi/`, `qwen/`, `gemma/`.
2. **Copy an existing model as a starting point.** The `gpt2/` directory is the
   simplest reference; `llama/` shows the gated-weights (BuildKit secret)
   pattern. Each directory contains:
   - `Dockerfile`
   - `download_model.py` — bakes weights in at build time (usually unchanged)
   - `serve.py` — tiny offline HTTP server (usually unchanged)
   - `requirements.txt`
   - `README.md`
3. **Set the default `MODEL_ID`** via the `ARG MODEL_ID=...` in the Dockerfile.
4. **Write the model README** following the structure used by the others:
   overview table, build locally, run (air-gapped + internal-network), pull from
   Docker Hub, and a security section.
5. **Register it in CI.** Add the directory name to the `matrix.model` list in
   [`.github/workflows/docker-build.yml`](.github/workflows/docker-build.yml).
6. **Update the root README** "Available models" table.

### Dockerfile checklist

Every Dockerfile **must**:

- [ ] Download/cache weights at **build time** (`RUN python download_model.py`).
- [ ] Set `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`.
- [ ] Run as a **non-root** user.
- [ ] Use a **BuildKit secret** for any gated-model token (never `ENV`/`ARG`).
- [ ] Include **comments** explaining: adding model files, enforcing network
      isolation, and exposing the port.
- [ ] `EXPOSE` the inference port (documentation), and document the
      `--network none` air-gapped run path in the README.

## Improving an existing model

- Pin or bump dependency versions in `requirements.txt` with a short rationale in
  the PR.
- Keep `serve.py` / `download_model.py` consistent across models unless a model
  genuinely needs different behaviour (note it in the PR).

## Testing your change locally

```bash
# Build (network used here, at build time only)
docker build -t airlock-<model> ./<model>

# Verify it runs with NO network
docker run -d --name <model> --network none airlock-<model>
docker exec <model> python -c "import serve; print(serve.generate('Hello', 16))"

# Prove isolation: this MUST fail (no network interface)
docker exec <model> python -c "import socket; socket.create_connection(('huggingface.co', 443), 5)" \
  && echo 'LEAK: had network!' || echo 'OK: no network'
```

## Pull request process

1. Fork and create a feature branch.
2. Make your change; ensure `docker build ./<model>` succeeds locally.
3. Open a PR. CI will **build** (but not push) your model on the PR.
4. A maintainer reviews for the isolation guarantees above and merges.

By contributing you agree your work is released under the repo's
[MIT License](LICENSE). You are responsible for ensuring any model weights you
reference are permitted to be used/redistributed.
