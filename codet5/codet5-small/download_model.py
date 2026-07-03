"""Download and cache model weights at BUILD time.

The completed image contains the full Hugging Face snapshot, so inference does
not need network access. snapshot_download avoids loading the model during the
build and therefore keeps build-time memory use low.
"""
import os

from huggingface_hub import snapshot_download

MODEL_ID = os.environ["MODEL_ID"]
CACHE_DIR = os.environ.get("MODEL_CACHE", "/models")

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
