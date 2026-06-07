from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import html
import json
import os


PORT = 8103
FLAG = "FLAG_A02_SECURITY_MISCONFIGURATION_SUCCESS"


def esc(v):
    return html.escape(str(v), quote=True)


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;text-decoration:none;color:#172026}pre{background:#eef1f2;padding:12px;border-radius:6px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | InkPress</title><style>{css}</style></head><body><header><h1>InkPress</h1><p>Blog and publishing platform</p><nav><a href='/'>Home</a><a href='/posts'>Posts</a><a href='/debug'>Diagnostics</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self.send(page("Home", "<h2>Publish essays and product stories</h2><p>InkPress is a small publishing site with editorial support tooling.</p>"))
        if path == "/posts":
            return self.send(page("Posts", "<h2>Latest Posts</h2><article><h3>How to choose a keyboard</h3><p>Practical buying advice for remote workers.</p></article>"))
        if path == "/debug":
            payload = {"site": "InkPress", "debug": True, "env": {"APP_ENV": os.environ.get("APP_ENV", "production"), "SECRET_KEY": "dev-secret-key-leaked"}, "flag": FLAG}
            return self.send(page("Diagnostics", f"<h2>Publishing Diagnostics</h2><p>Debug data is public.</p><pre>{esc(json.dumps(payload, indent=2))}</pre><pre class='flag'>{FLAG}</pre>"))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("X-Debug-Mode", "true"); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"InkPress running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
