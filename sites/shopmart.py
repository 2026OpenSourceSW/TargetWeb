from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import html
import sqlite3


PORT = 8101
FLAG = "FLAG_A01_BROKEN_ACCESS_CONTROL_SUCCESS"


def db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
    CREATE TABLE users (id INTEGER, username TEXT, role TEXT, email TEXT, api_key TEXT);
    CREATE TABLE orders (id INTEGER, user_id INTEGER, title TEXT, amount INTEGER, card_hint TEXT);
    INSERT INTO users VALUES (1,'alice','customer','alice@example.test','ak_alice_demo');
    INSERT INTO users VALUES (2,'bob','customer','bob@example.test','ak_bob_demo');
    INSERT INTO orders VALUES (1001,1,'Wireless Keyboard',96,'4111-1111-1111-1111');
    INSERT INTO orders VALUES (1002,2,'Gaming Monitor',420,'5555-2222-3333-4444');
    """)
    return conn


DB = db()


def esc(v):
    return html.escape(str(v), quote=True)


def table(rows):
    if not rows:
        return "<p>No records found.</p>"
    headers = rows[0].keys()
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{esc(r[h])}</td>" for h in headers) + "</tr>" for r in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | ShopMart</title><style>
body{{margin:0;font-family:Arial,sans-serif;color:#172026}}header{{background:#eef6f4;border-bottom:1px solid #d9e1e5}}.wrap{{max-width:1080px;margin:auto;padding:18px}}
nav a,.button{{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;text-decoration:none;color:#172026}}.button,button{{background:#0f766e;color:#fff;border-color:#0b5f59}}
.hero,.card{{border:1px solid #d9e1e5;border-radius:8px;padding:18px;margin:16px 0}}input{{padding:9px;width:100%;border:1px solid #b9c4ca;border-radius:6px}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #d9e1e5;padding:8px;text-align:left}}.flag{{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;padding:12px;border-radius:6px;font-weight:bold}}
</style></head><body><header><div class="wrap"><h1>ShopMart</h1><p>Online shopping for electronics and office gear</p><nav><a href="/">Home</a><a href="/account?user_id=1">Profile</a><a href="/order?order_id=1001">Orders</a></nav></div></header><main class="wrap">{body}</main></body></html>""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path == "/":
            body = """<section class="hero"><h2>Deals on work-from-home gear</h2><p>ShopMart lets customers manage profiles and receipts.</p></section>
            <section class="card"><h3>My Profile</h3><a class="button" href="/account?user_id=1">Open profile</a></section>
            <section class="card"><h3>Order Receipt</h3><a class="button" href="/order?order_id=1001">Open receipt</a></section>"""
            return self.send(page("Home", body))
        if parsed.path == "/account":
            user_id = qs.get("user_id", ["1"])[0]
            rows = DB.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchall()
            body = f"""<h2>My Account</h2><p>Signed in as Alice. The support selector trusts the customer_id parameter.</p>
            <form><label>Customer ID <input name="user_id" value="{esc(user_id)}"></label><button>Load profile</button></form>{table(rows)}
            {'<pre class="flag">'+FLAG+'</pre>' if user_id != '1' and rows else ''}"""
            return self.send(page("My Account", body))
        if parsed.path == "/order":
            order_id = qs.get("order_id", ["1001"])[0]
            rows = DB.execute(f"SELECT * FROM orders WHERE id = {order_id}").fetchall()
            hit = any(r["user_id"] != 1 for r in rows)
            body = f"""<h2>Order Receipt</h2><p>Receipt lookup does not verify customer ownership.</p>
            <form><label>Order ID <input name="order_id" value="{esc(order_id)}"></label><button>Open receipt</button></form>{table(rows)}
            {'<pre class="flag">'+FLAG+'</pre>' if hit else ''}"""
            return self.send(page("Order Receipt", body))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    print(f"ShopMart running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
