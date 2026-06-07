from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse
import html


PORT = 8104
FLAG = "FLAG_A02_SECURITY_MISCONFIGURATION_SUCCESS"
FILES = {
    "public/about.txt": "Public portfolio information.",
    "public/shipping.txt": "Print shipping takes 2-4 business days.",
    "private/admin-api-key.txt": f"admin_api_key=frameshare-demo-admin\n{FLAG}",
}


def esc(v):
    return html.escape(str(v), quote=True)


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a,button{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;background:#0f766e;color:white;text-decoration:none}input{width:100%;padding:9px}pre{background:#eef1f2;padding:12px;border-radius:6px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | FrameShare</title><style>{css}</style></head><body><header><h1>FrameShare</h1><p>Photo portfolio and file gallery</p><nav><a href='/'>Home</a><a href='/files?file=public/about.txt'>Files</a><a href='/preview-api'>Preview API</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path); qs = parse_qs(parsed.query)
        if parsed.path == "/":
            return self.send(page("Home", "<h2>Minimal photo portfolio hosting</h2><p>Publish galleries and share downloadable files.</p>"))
        if parsed.path == "/files":
            name = unquote(qs.get("file", ["public/about.txt"])[0])
            links = "".join(f"<li><a href='/files?file={quote(k)}'>{esc(k)}</a></li>" for k in FILES)
            body = f"<h2>File Library</h2><form><input name='file' value='{esc(name)}'><button>Open file</button></form><ul>{links}</ul><pre>{esc(FILES.get(name, 'File not found.'))}</pre>{('<pre class=flag>'+FLAG+'</pre>') if name.startswith('private/') else ''}"
            return self.send(page("Files", body))
        if parsed.path == "/preview-api":
            return self.send(page("Preview API", f"<h2>Gallery Preview API</h2><pre>Access-Control-Allow-Origin: *\nX-Debug-Mode: true</pre><pre class='flag'>{FLAG}</pre>"))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("X-Debug-Mode", "true"); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"FrameShare running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
