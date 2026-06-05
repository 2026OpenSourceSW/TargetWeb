from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import html


PORT = 8110
FLAG = "FLAG_A05_INJECTION_SUCCESS"
COMMENTS = [("editor", "Welcome to the daily post")]


def esc(v):
    return html.escape(str(v), quote=True)


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a,button{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;background:#0f766e;color:white;text-decoration:none}input,textarea{width:100%;padding:9px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;padding:12px;border-radius:6px;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | NewsNest</title><style>{css}</style></head><body><header><h1>NewsNest</h1><p>Blog and news website</p><nav><a href='/'>Home</a><a href='/comments'>Comments</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path == "/":
            return self.send(page("Home", "<h2>Independent daily news and notes</h2><p>NewsNest publishes short posts and accepts reader comments.</p>"))
        if urlparse(self.path).path == "/comments":
            return self.render("")
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def do_POST(self):
        if urlparse(self.path).path == "/comments":
            length = int(self.headers.get("Content-Length", "0"))
            form = parse_qs(self.rfile.read(length).decode())
            COMMENTS.append((form.get("author", ["guest"])[0], form.get("body", [""])[0]))
            return self.render("Comment posted.")
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def render(self, msg):
        rendered = "".join(f"<p><strong>{a}</strong>: {b}</p>" for a, b in COMMENTS)
        hit = any("<script" in b.lower() or "onerror" in b.lower() for _a, b in COMMENTS)
        body = f"<h2>Reader Comments</h2><form method='post'><input name='author' value='guest'><textarea name='body'>&lt;script&gt;alert('news')&lt;/script&gt;</textarea><button>Post comment</button></form><p>{esc(msg)}</p><section>{rendered}</section>{('<pre class=flag>'+FLAG+'</pre>') if hit else ''}"
        self.send(page("Comments", body))

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"NewsNest running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
