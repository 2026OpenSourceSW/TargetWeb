from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import html
import sqlite3


PORT = 8109
FLAG = "FLAG_A05_INJECTION_SUCCESS"
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.row_factory = sqlite3.Row
DB.executescript("""
CREATE TABLE books (id INTEGER, title TEXT, author TEXT, category TEXT, price INTEGER);
CREATE TABLE reviews (author TEXT, body TEXT);
INSERT INTO books VALUES (1,'Python for Teams','Dana Lee','technology',32);
INSERT INTO books VALUES (2,'Secure Web Patterns','Mina Cho','technology',41);
INSERT INTO books VALUES (3,'Holiday Cooking','Soo Han','lifestyle',24);
INSERT INTO books VALUES (4,'Admin Only Draft','Internal','hidden',1);
INSERT INTO reviews VALUES ('alice','Great packaging and fast delivery');
""")


def esc(v):
    return html.escape(str(v), quote=True)


def table(rows):
    if not rows:
        return "<p>No books found.</p>"
    keys = rows[0].keys()
    return "<table><tr>" + "".join(f"<th>{esc(k)}</th>" for k in keys) + "</tr>" + "".join("<tr>" + "".join(f"<td>{esc(r[k])}</td>" for k in keys) + "</tr>" for r in rows) + "</table>"


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a,button{display:inline-block;margin:4px;padding:8px 12px;border:1px solid #d9e1e5;border-radius:6px;background:#0f766e;color:white;text-decoration:none}input,textarea{width:100%;padding:9px}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ddd;padding:8px}pre{background:#eef1f2;padding:12px;border-radius:6px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;font-weight:bold}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | BookBarn</title><style>{css}</style></head><body><header><h1>BookBarn</h1><p>Online bookstore</p><nav><a href='/'>Home</a><a href='/search?q=python'>Search</a><a href='/reviews'>Reviews</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path); qs = parse_qs(parsed.query)
        if parsed.path == "/":
            return self.send(page("Home", "<h2>Books for practical people</h2><p>BookBarn has a catalog search and customer review board.</p>"))
        if parsed.path == "/search":
            term = qs.get("q", ["python"])[0]
            sql = f"SELECT id, title, author, category, price FROM books WHERE title LIKE '%{term}%' OR category LIKE '%{term}%'"
            hit = "' OR '1'='1" in term or "UNION" in term.upper()
            try:
                rows = DB.execute(sql).fetchall(); msg = ""
            except Exception as exc:
                rows = []; msg = f"SQL error: {exc}"
            body = f"<h2>Book Search</h2><form><input name='q' value='{esc(term)}'><button>Search</button></form><pre>{esc(sql)}</pre><p>{esc(msg)}</p>{table(rows)}{('<pre class=flag>'+FLAG+'</pre>') if hit else ''}"
            return self.send(page("Search", body))
        if parsed.path == "/reviews":
            return self.render_reviews("")
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def do_POST(self):
        if urlparse(self.path).path == "/reviews":
            length = int(self.headers.get("Content-Length", "0"))
            form = parse_qs(self.rfile.read(length).decode())
            DB.execute("INSERT INTO reviews VALUES (?, ?)", (form.get("author", ["reader"])[0], form.get("body", [""])[0]))
            DB.commit()
            return self.render_reviews("Review saved.")
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def render_reviews(self, msg):
        rows = DB.execute("SELECT author, body FROM reviews").fetchall()
        rendered = "".join(f"<p><strong>{r['author']}</strong>: {r['body']}</p>" for r in rows)
        hit = any("<script" in r["body"].lower() or "onerror" in r["body"].lower() for r in rows)
        body = f"<h2>Customer Reviews</h2><form method='post'><input name='author' value='reader'><textarea name='body'>&lt;img src=x onerror=alert('stored')&gt;</textarea><button>Save review</button></form><p>{esc(msg)}</p><section>{rendered}</section>{('<pre class=flag>'+FLAG+'</pre>') if hit else ''}"
        self.send(page("Reviews", body))

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"BookBarn running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
