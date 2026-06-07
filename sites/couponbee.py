from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import html


PORT = 8111
FLAG = "FLAG_A05_INJECTION_SUCCESS"


def esc(v):
    return html.escape(str(v), quote=True)


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a,button{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;background:#0f766e;color:white;text-decoration:none}input{width:100%;padding:9px}.card{border:1px solid #d9e1e5;border-radius:8px;padding:16px;margin:16px 0}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;padding:12px;border-radius:6px;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | CouponBee</title><style>{css}</style></head><body><header><h1>CouponBee</h1><p>Promotion and coupon website</p><nav><a href='/'>Home</a><a href='/greeting?name=buyer'>Greeting</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path); qs = parse_qs(parsed.query)
        if parsed.path == "/":
            return self.send(page("Home", "<h2>Coupons personalized for every shopper</h2><p>CouponBee previews campaign landing pages before sending email offers.</p>"))
        if parsed.path == "/greeting":
            name = qs.get("name", ["buyer"])[0]
            hit = "<script" in name.lower()
            body = f"<h2>Coupon Greeting Preview</h2><form><input name='name' value='{esc(name)}'><button>Preview</button></form><section class='card'><h3>Welcome back, {name}</h3><p>Your 20% coupon is ready.</p></section>{('<pre class=flag>'+FLAG+'</pre>') if hit else ''}"
            return self.send(page("Greeting", body))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"CouponBee running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
