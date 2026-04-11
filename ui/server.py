from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


HOST = os.getenv("UI_HOST", "127.0.0.1")
PORT = int(os.getenv("UI_PORT", "3000"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/chat")
BACKEND_TIMEOUT = float(os.getenv("BACKEND_TIMEOUT_SECONDS", "120"))
BASE_DIR = Path(__file__).resolve().parent


class ChatUIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_POST(self) -> None:
        if self.path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND, "Route not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.respond_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Expected a valid JSON body."},
            )
            return

        message = str(payload.get("message", "")).strip()
        thread_id = str(payload.get("threadId", "")).strip()

        if not message or not thread_id:
            self.respond_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Both message and threadId are required."},
            )
            return

        backend_body = json.dumps(
            {"user": message, "thread_id": thread_id}
        ).encode("utf-8")
        backend_request = Request(
            BACKEND_URL,
            data=backend_body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )

        try:
            with urlopen(backend_request, timeout=BACKEND_TIMEOUT) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body or "{}")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            self.respond_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "error": "The backend returned an error.",
                    "details": detail,
                },
            )
            return
        except URLError as error:
            self.respond_json(
                HTTPStatus.BAD_GATEWAY,
                {
                    "error": "Could not reach the FastAPI backend.",
                    "details": str(error.reason),
                },
            )
            return
        except json.JSONDecodeError:
            self.respond_json(
                HTTPStatus.BAD_GATEWAY,
                {"error": "The backend response was not valid JSON."},
            )
            return

        self.respond_json(HTTPStatus.OK, data)

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def respond_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), ChatUIHandler)
    print(f"UI server running at http://{HOST}:{PORT}")
    print(f"Proxying chat requests to {BACKEND_URL}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nUI server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
