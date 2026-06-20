# syntax=docker/dockerfile:1
# =============================================================================
# Gemma 4 12B (Google) -- fully offline inference image, 4-bit GGUF / llama.cpp
# -----------------------------------------------------------------------------
# Open weights (Apache-2.0): builds with NO credentials. Unlike the rest of the
# repo (transformers + full-precision safetensors), Gemma 4 is served from a
# single 4-bit GGUF via llama.cpp -- the same quantization Ollama's `gemma4:12b`
# ships -- so the image is ~8 GB instead of ~28 GB and runs well on CPU.
#
# Gemma 4 is a multimodal model; this server uses it text-in / text-out.
#
# Isolation strategy (two layers):
#   1. BUILD time : the GGUF is downloaded ONCE and baked into the image, so the
#                   running container never needs to fetch anything.
#   2. RUN  time  : HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE hard-disable any
#                   accidental outbound calls, and the image is meant to be run
#                   with `docker run --network none` (see README) which removes
#                   networking from the container completely.
# =============================================================================

FROM python:3.11-slim

# ---- Build-time configuration ----------------------------------------------
# Override at build time with: --build-arg MODEL_ID=<gguf-repo> --build-arg MODEL_FILE=<file.gguf>
ARG MODEL_ID=unsloth/gemma-4-12b-it-GGUF
ARG MODEL_FILE=gemma-4-12b-it-Q4_K_M.gguf
ENV MODEL_ID=${MODEL_ID} \
    MODEL_FILE=${MODEL_FILE} \
    MODEL_CACHE=/models \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- Python dependencies ---------------------------------------------------
# NOTE: the network is used HERE, at build time only. Prebuilt CPU wheels mean
# no C/C++ toolchain is needed in the image (see requirements.txt).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Add model files -------------------------------------------------------
# Download and cache the single GGUF INTO the image so the container is fully
# self-contained and never reaches the network at runtime.
COPY download_model.py .
RUN python download_model.py

# ---- Application code -------------------------------------------------------
COPY serve.py .

# ---- Enforce network isolation at runtime ----------------------------------
# Force the HuggingFace stack offline so even a misconfigured run cannot phone
# home. The strongest guarantee still comes from `docker run --network none`.
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

# ---- Expose the inference port ---------------------------------------------
# EXPOSE is documentation only. With `--network none` there is no network at
# all -- reach the model via `docker exec`/mounted volumes, OR run it on a
# dedicated internal bridge network that has no internet egress (see README).
EXPOSE 8000

# ---- Drop privileges (defense in depth) ------------------------------------
RUN useradd --create-home appuser && chown -R appuser /app /models
USER appuser

CMD ["python", "serve.py"]
