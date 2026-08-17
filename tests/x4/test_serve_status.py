from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from x4.serve import Handler


def test_status_endpoint_reports_governance() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/api/x4/status"
        with urllib.request.urlopen(url, timeout=3) as response:
            payload = json.loads(response.read().decode())
        assert payload["service"] == "x4-arsenal"
        assert payload["governance"] == "enforced"
    finally:
        server.shutdown()
        server.server_close()
