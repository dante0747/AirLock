"""Download and cache model weights at BUILD time.

This script runs once, inside `docker build`, so the finished image already
contains everything the model needs. The running container therefore never has
to reach the network to fetch weights -- a hard requirement for the offline /
air-gapped runtime this repo targets.

We use snapshot_download (NOT AutoModel.from_pretrained) on purpose: it fetches
the repo files straight into the HuggingFace cache WITHOUT instantiating the
model in RAM. Loading a multi-billion-parameter model just to cache it can need
~2x the model size in memory and OOM small build hosts / CI runners with
"cannot allocate memory". serve.py loads the model from this same cache at
runtime. For MiniMax-M3 the snapshot also includes the custom modeling *.py
files, which serve.py executes via trust_remote_code -- from this cache, so the
runtime stays fully offline.

The model id is taken from the MODEL_ID environment variable (set by the
Dockerfile via a build ARG). An optional HuggingFace access token is read from
a BuildKit secret (/run/secrets/hf_token) or the HF_TOKEN env var; it is only
needed for gated models (e.g. official Llama / Mistral weights) and is never
baked into the final image.
"""
import os

from huggingface_hub import snapshot_download

MODEL_ID = os.environ["MODEL_ID"]
CACHE_DIR = os.environ.get("MODEL_CACHE", "/models")

# Weight formats transformers never loads on this CPU stack. Skipping them keeps
# the image smaller and the download faster (e.g. GGUF, TF/Flax, raw Llama
# "original/" consolidated checkpoints).
IGNORE_PATTERNS = [
    "*.gguf",
    "*.pt",
    "*.pth",
    "*.onnx",
    "*.onnx_data",
    "*.msgpack",
    "*.h5",
    "original/**",
    "consolidated*",
]


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
    print(f"[download] Fetching '{MODEL_ID}' into '{CACHE_DIR}' ...", flush=True)
    snapshot_download(
        repo_id=MODEL_ID,
        cache_dir=CACHE_DIR,
        token=get_token(),
        ignore_patterns=IGNORE_PATTERNS,
    )
    print("[download] Done. Weights are now baked into the image.", flush=True)


if __name__ == "__main__":
    main()
