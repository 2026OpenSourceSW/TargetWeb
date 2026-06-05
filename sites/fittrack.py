from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import base64
import hashlib
import html
import time


PORT = 8107
FLAG = "FLAG_A04_CRYPTO_FAILURE_SUCCESS"


def esc(v):
    return html.escape(str(v), quote=True)


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a,button{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;background:#0f766e;color:white;text-decoration:none}input{width:100%;padding:9px}pre{background:#eef1f2;padding:12px;border-radius:6px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | FitTrack</title><style>{css}</style></head><body><header><h1>FitTrack</h1><p>Fitness membership website</p><nav><a href='/'>Home</a><a href='/session?user=alice'>Session</a><a href='/reset?user_id=1'>Reset</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path); qs = parse_qs(parsed.query)
        if parsed.path == "/":
            return self.send(page("Home", "<h2>Personal fitness classes and memberships</h2><p>FitTrack lets members review mobile session tokens.</p>"))
        if parsed.path == "/session":
            user = qs.get("user", ["alice"])[0]
            role = "admin" if user == "admin" else "member"
            payload = f"user={user}&role={role}" + (f"&flag={FLAG}" if user == "admin" else "")
            token = base64.urlsafe_b64encode(payload.encode()).decode()
            decoded = base64.urlsafe_b64decode(token).decode()
            body = f"<h2>Mobile Session Token</h2><form><input name='user' value='{esc(user)}'><button>Create token</button></form><pre>{esc(token)}</pre><p>Decoded: <code>{esc(decoded)}</code></p>{('<pre class=flag>'+FLAG+'</pre>') if user == 'admin' else ''}"
            return self.send(page("Session Token", body))
        if parsed.path == "/reset":
            user_id = qs.get("user_id", ["1"])[0]
            token = hashlib.md5(f"{user_id}:{int(time.time() // 3600)}".encode()).hexdigest()[:10]
            return self.send(page("Password Reset", f"<h2>Password Reset</h2><form><input name='user_id' value='{esc(user_id)}'><button>Create token</button></form><pre>{token}</pre><pre class='flag'>{FLAG}</pre>"))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"FitTrack running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
