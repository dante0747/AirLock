# syntax=docker/dockerfile:1
# =============================================================================
# Mistral -- fully offline inference image
# -----------------------------------------------------------------------------
# Default model is the official Mistral-7B-Instruct, which is GATED: you must
# accept the license on HuggingFace and supply a token as a BuildKit secret.
# See README for an open, ungated alternative you can drop in for testing.
#
# Isolation strategy (two layers):
#   1. BUILD time : weights are downloaded ONCE and baked into the image, so the
#                   running container never needs to fetch anything.
#   2. RUN  time  : HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE hard-disable any
#                   accidental outbound calls, and the image is meant to be run
#                   with `docker run --network none` (see README) which removes
#                   networking from the container completely.
# =============================================================================

FROM python:3.11-slim

# ---- Build-time configuration ----------------------------------------------
# Gated default; supply a token via BuildKit secret (see README). Override with
# an open model for credential-free testing, e.g.:
#   docker build --build-arg MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0 ...
ARG MODEL_ID=mistralai/Mistral-7B-Instruct-v0.2
ENV MODEL_ID=${MODEL_ID} \
    MODEL_CACHE=/models \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- Python dependencies ---------------------------------------------------
# NOTE: the network is used HERE, at build time only.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Add model files -------------------------------------------------------
# Download and cache the weights INTO the image so the container is fully
# self-contained and never reaches the network at runtime. The hf_token secret
# is optional (required=false) but needed for the gated default; because it is
# mounted as a BuildKit secret it is NEVER written into an image layer.
COPY download_model.py .
RUN --mount=type=secret,id=hf_token,required=false \
    python download_model.py

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
