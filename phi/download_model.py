"""Download and cache model weights at BUILD time.

This script runs once, inside `docker build`, so the finished image already
contains everything the model needs. The running container therefore never has
to reach the network to fetch weights -- a hard requirement for the offline /
air-gapped runtime this repo targets.

The model id is taken from the MODEL_ID environment variable (set by the
Dockerfile via a build ARG). An optional HuggingFace access token is read from
a BuildKit secret (/run/secrets/hf_token) or the HF_TOKEN env var; it is only
needed for gated models (e.g. official Llama / Mistral weights) and is never
baked into the final image.
"""
import os

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = os.environ["MODEL_ID"]
CACHE_DIR = os.environ.get("MODEL_CACHE", "/models")


def get_token():
    """Return an HF token from a BuildKit secret or env var, if provided."""
    secret_path = "/run/secrets/hf_token"
    if os.path.exists(secret_path):
        with open(secret_path, encoding="utf-8") as handle:
            token = handle.read().strip()
            if token:
                return token
    return os.environ.get("HF_TOKEN") or None


def main():
    kwargs = {"cache_dir": CACHE_DIR}
    token = get_token()
    if token:
        kwargs["token"] = token

    print(f"[download] Fetching '{MODEL_ID}' into '{CACHE_DIR}' ...", flush=True)
    AutoTokenizer.from_pretrained(MODEL_ID, **kwargs)
    AutoModelForCausalLM.from_pretrained(MODEL_ID, **kwargs)
    print("[download] Done. Weights are now baked into the image.", flush=True)


if __name__ == "__main__":
    main()
