import base64
import json
import os
import random
import sqlite3
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


PORT = int(os.environ.get("PORT", "3010"))
ROOT_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT_DIR / "public"
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "marketnest.db"

USERS = [
    {
        "id": 1,
        "role": "customer",
        "name": "Jin Woo",
        "email": "jinwoo@example.com",
        "password": "password123",
        "apiKey": "cust_live_plaintext_7f4d2b",
        "cardNumber": "4111111111111111",
        "cvv": "123",
    },
    {
        "id": 2,
        "role": "admin",
        "name": "Admin Mina",
        "email": "admin@example.com",
        "password": "admin123",
        "apiKey": "admin_live_plaintext_99a81c",
        "cardNumber": "5555555555554444",
        "cvv": "999",
    },
]

PRODUCTS = [
    {
        "id": 101,
        "name": "Nimbus Sneakers",
        "category": "shoes",
        "price": 89000,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
        "description": "Lightweight knit sneakers for daily city walking.",
    },
    {
        "id": 102,
        "name": "Aurora Headphones",
        "category": "electronics",
        "price": 129000,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
        "description": "Wireless over-ear headphones with rich bass.",
    },
    {
        "id": 103,
        "name": "Canvas Weekender",
        "category": "bags",
        "price": 72000,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
        "description": "Compact travel bag with laptop sleeve.",
    },
    {
        "id": 104,
        "name": "Ceramic Pour-over Set",
        "category": "home",
        "price": 54000,
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
        "description": "Slow coffee kit for a clean morning brew.",
    },
    {
        "id": 105,
        "name": "Metro Smartwatch",
        "category": "electronics",
        "price": 174000,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
        "description": "Activity tracking and notification companion.",
    },
    {
        "id": 106,
        "name": "Linen Overshirt",
        "category": "fashion",
        "price": 63000,
        "image": "https://images.unsplash.com/photo-1520975954732-35dd22299614?auto=format&fit=crop&w=900&q=80",
        "description": "Breathable overshirt for layered outfits.",
    },
]

ORDERS = [
    {"id": 9001, "userId": 1, "total": 218000, "status": "paid", "items": ["Nimbus Sneakers", "Aurora Headphones"]},
    {"id": 9002, "userId": 2, "total": 54000, "status": "internal-review", "items": ["Ceramic Pour-over Set"]},
]

REVIEWS = [
    {"productId": 101, "author": "soyeon", "body": "Comfortable enough for a full day out."},
    {"productId": 102, "author": "minjae", "body": "Battery lasts longer than expected."},
]

SESSIONS = {}


def initialize_database():
    DATA_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              category TEXT NOT NULL,
              price INTEGER NOT NULL,
              image TEXT NOT NULL,
              description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS customer_private_notes (
              id INTEGER PRIMARY KEY,
              email TEXT NOT NULL,
              memo TEXT NOT NULL
            );

            DELETE FROM products;
            DELETE FROM customer_private_notes;
            """
        )
        conn.executemany(
            """
            INSERT INTO products (id, name, category, price, image, description)
            VALUES (:id, :name, :category, :price, :image, :description)
            """,
            PRODUCTS,
        )
        conn.executemany(
            "INSERT INTO customer_private_notes (id, email, memo) VALUES (?, ?, ?)",
            [
                (1, "jinwoo@example.com", "VIP coupon code: NEST-VIP-70"),
                (2, "admin@example.com", "Back-office approval memo: refund manually"),
            ],
        )


def query_all(sql):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql).fetchall()]


def make_session(user):
    raw = f"{user['id']}:{int(time.time() * 1000)}"
    token = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    SESSIONS[token] = {
        "id": user["id"],
        "role": user["role"],
        "name": user["name"],
        "email": user["email"],
    }
    return token


def parse_cookie(header):
    cookies = {}
    for part in header.split(";"):
        if "=" in part:
            key, value = part.strip().split("=", 1)
            cookies[key] = value
    return cookies


class MarketNestHandler(BaseHTTPRequestHandler):
    server_version = "MarketNest/1.0"

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.handle_api()
        else:
            self.serve_static()

    def do_POST(self):
        self.handle_api()

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            return {"malformedBody": raw, "parseError": str(error)}

    def current_session(self):
        cookies = parse_cookie(self.headers.get("Cookie", ""))
        token = cookies.get("session")
        return SESSIONS.get(token)

    def serve_static(self):
        parsed = urlparse(self.path)
        route_aliases = {
            "/categories": "/product.html",
            "/categories/": "/product.html",
            "/cart": "/checkout.html",
            "/cart/": "/checkout.html",
            "/account": "/login.html",
            "/account/": "/login.html",
        }
        requested = route_aliases.get(parsed.path, "/index.html" if parsed.path == "/" else unquote(parsed.path))
        relative = requested.lstrip("/")
        file_path = (PUBLIC_DIR / relative).resolve()

        if not str(file_path).startswith(str(PUBLIC_DIR.resolve())):
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_types.get(file_path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_api(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        session = self.current_session()

        try:
            if self.command == "POST" and parsed.path == "/api/login":
                return self.login()

            if self.command == "POST" and parsed.path == "/api/signup":
                return self.signup()

            if self.command == "POST" and parsed.path == "/api/logout":
                cookies = parse_cookie(self.headers.get("Cookie", ""))
                token = cookies.get("session")
                if token:
                    SESSIONS.pop(token, None)
                return self.send_json(HTTPStatus.OK, {"ok": True}, {"Set-Cookie": "session=; Path=/; Max-Age=0"})

            if parsed.path == "/api/me":
                return self.send_json(HTTPStatus.OK, {"user": session})

            if parsed.path == "/api/products":
                return self.send_json(HTTPStatus.OK, {"products": query_all("SELECT * FROM products ORDER BY id")})

            if parsed.path == "/api/product":
                product_id = int(query.get("id", ["0"])[0])
                products = query_all(f"SELECT * FROM products WHERE id = {product_id}")
                if not products:
                    return self.send_json(HTTPStatus.NOT_FOUND, {"error": "Product not found"})
                return self.send_json(HTTPStatus.OK, {"product": products[0]})

            if parsed.path == "/api/search":
                term = query.get("q", [""])[0]
                sql = f"SELECT * FROM products WHERE name LIKE '%{term}%' OR category LIKE '%{term}%'"
                try:
                    results = query_all(sql)
                    return self.send_json(HTTPStatus.OK, {"simulatedSql": sql, "results": results})
                except sqlite3.Error as error:
                    return self.send_json(HTTPStatus.OK, {"simulatedSql": sql, "results": [], "databaseError": str(error)})

            if parsed.path == "/api/reviews" and self.command == "GET":
                product_id = int(query.get("productId", ["0"])[0])
                reviews = [review for review in REVIEWS if review["productId"] == product_id]
                return self.send_json(HTTPStatus.OK, {"reviews": reviews})

            if parsed.path == "/api/reviews" and self.command == "POST":
                body = self.read_json()
                review = {
                    "productId": int(body.get("productId") or 0),
                    "author": body.get("author") or "anonymous",
                    "body": body.get("body") or "",
                }
                REVIEWS.append(review)
                return self.send_json(HTTPStatus.CREATED, {"review": review})

            if parsed.path == "/api/orders":
                user_id = int(query.get("userId", [session["id"] if session else 1])[0])
                orders = [order for order in ORDERS if order["userId"] == user_id]
                return self.send_json(HTTPStatus.OK, {"orders": orders})

            if parsed.path == "/api/order":
                order_id = int(query.get("orderId", ["0"])[0])
                order = next((item for item in ORDERS if item["id"] == order_id), None)
                if not order:
                    return self.send_json(HTTPStatus.NOT_FOUND, {"error": "Order not found"})
                return self.send_json(HTTPStatus.OK, {"order": order})

            if parsed.path == "/api/admin/orders":
                return self.send_json(HTTPStatus.OK, {"orders": ORDERS, "currentUser": session})

            if parsed.path == "/api/admin/products":
                return self.send_json(HTTPStatus.OK, {"products": query_all("SELECT * FROM products ORDER BY id")})

            if parsed.path == "/api/checkout" and self.command == "POST":
                return self.checkout(session)

            if parsed.path == "/api/internal/customer":
                customers = [
                    {
                        "id": user["id"],
                        "email": user["email"],
                        "password": user["password"],
                        "apiKey": user["apiKey"],
                        "cardNumber": user["cardNumber"],
                        "cvv": user["cvv"],
                    }
                    for user in USERS
                ]
                return self.send_json(HTTPStatus.OK, {"customers": customers})

            if parsed.path == "/api/internal/env":
                return self.send_json(
                    HTTPStatus.OK,
                    {
                        "pythonVersion": os.sys.version,
                        "platform": os.name,
                        "cwd": os.getcwd(),
                        "envSample": {
                            "NODE_ENV": os.environ.get("NODE_ENV", "development"),
                            "PORT": PORT,
                            "SECRET_KEY": "dev-secret-key-checked-into-demo",
                        },
                        "headers": dict(self.headers),
                    },
                )

            if parsed.path == "/api/error":
                raise RuntimeError("Unexpected catalog service failure.")

            return self.send_json(HTTPStatus.NOT_FOUND, {"error": "API route not found"})
        except Exception as error:
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error), "stack": repr(error)})

    def login(self):
        body = self.read_json()
        user = next(
            (
                candidate
                for candidate in USERS
                if candidate["email"] == body.get("email") and candidate["password"] == body.get("password")
            ),
            None,
        )
        if not user:
            return self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "Invalid email or password"})

        token = make_session(user)
        return self.send_json(HTTPStatus.OK, {"user": SESSIONS[token]}, {"Set-Cookie": f"session={token}; Path=/"})

    def signup(self):
        body = self.read_json()
        if not body.get("name") or not body.get("email") or not body.get("password"):
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Name, email, and password are required."})

        if any(candidate["email"] == body.get("email") for candidate in USERS):
            return self.send_json(HTTPStatus.CONFLICT, {"error": "Email already exists."})

        user = {
            "id": len(USERS) + 1,
            "role": "customer",
            "name": body["name"],
            "email": body["email"],
            "password": body["password"],
            "apiKey": f"cust_live_plaintext_{os.urandom(3).hex()}",
            "cardNumber": body.get("cardNumber") or "4000000000000002",
            "cvv": body.get("cvv") or "000",
        }
        USERS.append(user)
        token = make_session(user)
        return self.send_json(HTTPStatus.CREATED, {"user": SESSIONS[token]}, {"Set-Cookie": f"session={token}; Path=/"})

    def checkout(self, session):
        body = self.read_json()
        client_total = float(body.get("clientTotal") or 0)
        discount_percent = float(body.get("discountPercent") or 0)
        final_total = round(client_total * (1 - discount_percent / 100))
        order = {
            "id": random.randint(10000, 99999),
            "userId": session["id"] if session else 1,
            "total": final_total,
            "status": "paid",
            "items": body.get("items") or [],
        }
        ORDERS.append(order)
        return self.send_json(HTTPStatus.CREATED, {"order": order})


def main():
    initialize_database()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), MarketNestHandler)
    print(f"MarketNest running at http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
