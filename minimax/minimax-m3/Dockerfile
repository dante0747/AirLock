# syntax=docker/dockerfile:1
# =============================================================================
# MiniMax-M3 (MiniMax AI) -- fully offline inference image
# -----------------------------------------------------------------------------
# Open weights (Apache-2.0): this image builds with NO credentials. MiniMax-M3
# is a large Mixture-of-Experts reasoning model, so the baked-in weights -- and
# therefore the image -- are big. Override MODEL_ID with a smaller model for a
# quick credential-free smoke test (see README).
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
# Override the model at build time with: --build-arg MODEL_ID=<hf-model-id>
ARG MODEL_ID=MiniMaxAI/MiniMax-M3
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
# self-contained and never reaches the network at runtime. snapshot_download
# also pulls the model's custom modeling code (*.py), which serve.py loads via
# trust_remote_code at runtime -- entirely from this baked-in cache, never the
# network.
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
