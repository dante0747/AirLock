"""Minimal OFFLINE inference server for Gemma 4 (Python standard library + llama.cpp).

Loads the 4-bit GGUF that was baked into the image at build time and exposes a
tiny HTTP API. Crucially, it makes **no outbound network calls**:

  * The model is loaded from a local file path -- nothing is fetched from the
    Hub. HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE (set in the Dockerfile) add a
    belt-and-braces guard against any accidental "phone home".
  * The server is meant to be run with `docker run --network none`, which
    removes networking from the container entirely.

Gemma 4 is served text-in / text-out via llama.cpp's chat completion, which
applies the chat template embedded in the GGUF metadata -- so just send the raw
instruction as the prompt.

Endpoints:
  GET  /health    -> {"status": "ok", "model": "..."}
  POST /generate  -> body {"prompt": "...", "max_new_tokens": 128}
                     returns {"model": "...", "completion": "..."}
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from llama_cpp import Llama

MODEL_ID = os.environ["MODEL_ID"]
MODEL_FILE = os.environ["MODEL_FILE"]
CACHE_DIR = os.environ.get("MODEL_CACHE", "/models")
MODEL_PATH = os.path.join(CACHE_DIR, MODEL_FILE)
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
N_CTX = int(os.environ.get("N_CTX", "4096"))

print(f"[serve] Loading '{MODEL_PATH}' (offline) ...", flush=True)
llm = Llama(model_path=MODEL_PATH, n_ctx=N_CTX, verbose=False)


def generate(prompt: str, max_new_tokens: int = 128) -> str:
    result = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_new_tokens,
    )
    return result["choices"][0]["message"]["content"]


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
