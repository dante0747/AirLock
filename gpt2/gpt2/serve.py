"""Minimal OFFLINE inference server (Python standard library only).

Loads the model that was baked into the image at build time and exposes a tiny
HTTP API. Crucially, it makes **no outbound network calls**:

  * HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE (set in the Dockerfile) hard-disable
    any "phone home" behaviour in the HuggingFace stack.
  * The server is meant to be run with `docker run --network none`, which
    removes networking from the container entirely.

Endpoints:
  GET  /health    -> {"status": "ok", "model": "..."}
  POST /generate  -> body {"prompt": "...", "max_new_tokens": 128}
                     returns {"model": "...", "completion": "..."}
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = os.environ["MODEL_ID"]
CACHE_DIR = os.environ.get("MODEL_CACHE", "/models")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

print(f"[serve] Loading '{MODEL_ID}' (offline) ...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR, low_cpu_mem_usage=True)
model.eval()


def generate(prompt: str, max_new_tokens: int = 128) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 (http.server naming)
        if self.path == "/health":
            self._send(200, {"status": "ok", "model": MODEL_ID})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/generate":
            self._send(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid JSON body"})
            return
        prompt = data.get("prompt", "")
        max_new_tokens = int(data.get("max_new_tokens", 128))
        self._send(200, {"model": MODEL_ID, "completion": generate(prompt, max_new_tokens)})

    def log_message(self, *args):  # keep stdout clean
        pass


if __name__ == "__main__":
    print(f"[serve] Ready on {HOST}:{PORT} -- offline mode", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
