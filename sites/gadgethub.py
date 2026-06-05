from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import html


PORT = 8105
FLAG = "FLAG_A03_SUPPLY_CHAIN_SUCCESS"
DEPS = [
    ("jquery", "1.8.3", "3.7.1", "Known vulnerable storefront widget."),
    ("chart-lite", "2.1.0", "2.1.0 with SRI", "CDN script is loaded without integrity metadata."),
]


def esc(v):
    return html.escape(str(v), quote=True)


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;text-decoration:none;color:#172026}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ddd;padding:8px}pre{background:#eef1f2;padding:12px;border-radius:6px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | GadgetHub</title><style>{css}</style></head><body><header><h1>GadgetHub</h1><p>Consumer electronics storefront</p><nav><a href='/'>Home</a><a href='/assets'>Assets</a><a href='/deals-widget'>Deals Widget</a></nav></header><main>{body}</main></body></html>".encode()


def deps_table():
    rows = "".join(f"<tr><td>{esc(n)}</td><td>{esc(u)}</td><td>{esc(r)}</td><td>{esc(risk)}</td></tr>" for n, u, r, risk in DEPS)
    return "<table><tr><th>package</th><th>used</th><th>recommended</th><th>risk</th></tr>" + rows + "</table>"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self.send(page("Home", "<h2>New gadgets, daily markdowns</h2><p>GadgetHub is a storefront with a legacy asset dashboard.</p>"))
        if path == "/assets":
            return self.send(page("Assets", f"<h2>Storefront Asset Inventory</h2>{deps_table()}<pre class='flag'>{FLAG}</pre>"))
        if path == "/deals-widget":
            snippet = esc('<script src="https://cdn.example.test/chart-lite/2.1.0/chart.js"></script>')
            return self.send(page("Deals Widget", f"<h2>Deals Widget</h2><p>A third-party widget is loaded without SRI.</p><pre>{snippet}</pre><pre class='flag'>{FLAG}</pre>"))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"GadgetHub running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
