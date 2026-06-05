from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import html


PORT = 8106
FLAG = "FLAG_A03_SUPPLY_CHAIN_SUCCESS"


def esc(v):
    return html.escape(str(v), quote=True)


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a,button{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;background:#0f766e;color:white;text-decoration:none}input,select{width:100%;padding:9px}pre{background:#eef1f2;padding:12px;border-radius:6px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | CloudDesk</title><style>{css}</style></head><body><header><h1>CloudDesk</h1><p>SaaS workspace configuration</p><nav><a href='/'>Home</a><a href='/package-resolver'>Package Resolver</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path); qs = parse_qs(parsed.query)
        if parsed.path == "/":
            return self.send(page("Home", "<h2>Team support desk automation</h2><p>CloudDesk configures frontend packages for hosted workspaces.</p>"))
        if parsed.path == "/package-resolver":
            package = qs.get("package", ["left-pad-internal"])[0]
            source = qs.get("source", ["private-registry"])[0]
            hit = package == "left-pad-internal" and source == "public-registry"
            result = "Resolved from private-registry/left-pad-internal@0.0.2"
            if hit:
                result = "Resolved from public-registry/left-pad-internal@9.9.9 before the private package."
            body = f"<h2>Package Resolver</h2><form><input name='package' value='{esc(package)}'><select name='source'><option>private-registry</option><option {'selected' if source == 'public-registry' else ''}>public-registry</option></select><button>Resolve</button></form><pre>{esc(result)}</pre>{('<pre class=flag>'+FLAG+'</pre>') if hit else ''}"
            return self.send(page("Package Resolver", body))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"CloudDesk running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
