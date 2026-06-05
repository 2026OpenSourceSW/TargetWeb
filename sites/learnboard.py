from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import hashlib


PORT = 8108
FLAG = "FLAG_A04_CRYPTO_FAILURE_SUCCESS"
USERS = [
    ("alice", hashlib.md5(b"AlicePassword1!").hexdigest(), "alice@example.test"),
    ("bob", hashlib.md5(b"BobPassword1!").hexdigest(), "bob@example.test"),
    ("admin", hashlib.md5(b"AdminPassword1!").hexdigest(), "admin@example.test"),
]


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;text-decoration:none;color:#172026}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ddd;padding:8px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;padding:12px;border-radius:6px;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{title} | LearnBoard</title><style>{css}</style></head><body><header><h1>LearnBoard</h1><p>Online course community</p><nav><a href='/'>Home</a><a href='/users'>Users</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self.send(page("Home", "<h2>Short online classes for busy teams</h2><p>LearnBoard has a legacy account export page for instructors.</p>"))
        if path == "/users":
            rows = "".join(f"<tr><td>{u}</td><td>{h}</td><td>{e}</td></tr>" for u, h, e in USERS)
            return self.send(page("Users", f"<h2>User Directory</h2><p>Passwords are stored as fast MD5 hashes.</p><table><tr><th>username</th><th>password</th><th>email</th></tr>{rows}</table><pre class='flag'>{FLAG}</pre>"))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"LearnBoard running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
