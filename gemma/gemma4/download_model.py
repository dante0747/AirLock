"""Download and cache the GGUF weight file at BUILD time.

This script runs once, inside `docker build`, so the finished image already
contains everything the model needs. The running container therefore never has
to reach the network to fetch weights -- a hard requirement for the offline /
air-gapped runtime this repo targets.

Unlike the other models (which snapshot a whole transformers repo), Gemma 4 is
served from a single 4-bit GGUF, so we fetch just that one file with
hf_hub_download. serve.py loads it from this same cache directory at runtime.

The repo id and file name come from the MODEL_ID / MODEL_FILE environment
variables (set by the Dockerfile via build ARGs). The unsloth GGUF repo is
Apache-2.0 and NOT gated, so no token is needed; the optional HF_TOKEN env var
is still honoured if you point MODEL_ID at a gated GGUF repo instead.
"""
import os

from huggingface_hub import hf_hub_download

MODEL_ID = os.environ["MODEL_ID"]
MODEL_FILE = os.environ["MODEL_FILE"]
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
    print(f"[download] Fetching '{MODEL_FILE}' from '{MODEL_ID}' into '{CACHE_DIR}' ...", flush=True)
    path = hf_hub_download(
        repo_id=MODEL_ID,
        filename=MODEL_FILE,
        local_dir=CACHE_DIR,
        token=get_token(),
    )
    print(f"[download] Done. GGUF baked into the image at {path}.", flush=True)


if __name__ == "__main__":
    main()
