from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import html
import sqlite3


PORT = 8102
FLAG = "FLAG_A01_BROKEN_ACCESS_CONTROL_SUCCESS"


DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.row_factory = sqlite3.Row
DB.executescript("""
CREATE TABLE bookings (id INTEGER, user_id INTEGER, destination TEXT, traveler TEXT, total INTEGER);
INSERT INTO bookings VALUES (501,1,'Seoul','Alice Kim',280);
INSERT INTO bookings VALUES (502,2,'Tokyo','Bob Park',620);
""")


def esc(v):
    return html.escape(str(v), quote=True)


def table(rows):
    if not rows:
        return "<p>No booking found.</p>"
    keys = rows[0].keys()
    return "<table>" + "<tr>" + "".join(f"<th>{esc(k)}</th>" for k in keys) + "</tr>" + "".join("<tr>" + "".join(f"<td>{esc(r[k])}</td>" for k in keys) + "</tr>" for r in rows) + "</table>"


def page(title, body):
    css = "body{font-family:Arial;margin:0;color:#172026}header{background:#eef6f4;padding:18px}main{padding:24px;max-width:1000px;margin:auto}a,.button,button{padding:8px 12px;margin:4px;border-radius:6px;border:1px solid #d9e1e5;background:#0f766e;color:white;text-decoration:none}input{padding:9px;width:100%}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ddd;padding:8px}.flag{background:#fff1f2;color:#b91c1c;border:1px solid #fca5a5;padding:12px;border-radius:6px}"
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)} | TripNest</title><style>{css}</style></head><body><header><h1>TripNest</h1><p>Travel booking and itinerary management</p><nav><a href='/'>Home</a><a href='/booking?booking_id=501'>Bookings</a></nav></header><main>{body}</main></body></html>".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path == "/":
            return self.send(page("Home", "<h2>Book flexible weekend trips</h2><p>Find reservations and itinerary details.</p><p><a class='button' href='/booking?booking_id=501'>Find booking</a></p>"))
        if parsed.path == "/booking":
            booking_id = qs.get("booking_id", ["501"])[0]
            rows = DB.execute(f"SELECT * FROM bookings WHERE id = {booking_id}").fetchall()
            hit = any(r["user_id"] != 1 for r in rows)
            body = f"<h2>Booking Detail</h2><p>Booking ownership is not checked before returning traveler data.</p><form><input name='booking_id' value='{esc(booking_id)}'><button>Find booking</button></form>{table(rows)}{('<pre class=flag>'+FLAG+'</pre>') if hit else ''}"
            return self.send(page("Booking Detail", body))
        self.send(page("404", "<h2>Not found</h2>"), 404)

    def send(self, payload, status=200):
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)


if __name__ == "__main__":
    print(f"TripNest running at http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
