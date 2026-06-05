from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse
import base64
import hashlib
import html
import json
import os
import sqlite3
import time


HOST = os.environ.get("OWASP_LAB_HOST", "127.0.0.1")
PORT = int(os.environ.get("OWASP_LAB_PORT", "8000"))

FLAGS = {
    "A01": "FLAG_A01_BROKEN_ACCESS_CONTROL_SUCCESS",
    "A02": "FLAG_A02_SECURITY_MISCONFIGURATION_SUCCESS",
    "A03": "FLAG_A03_SUPPLY_CHAIN_SUCCESS",
    "A04": "FLAG_A04_CRYPTO_FAILURE_SUCCESS",
    "A05": "FLAG_A05_INJECTION_SUCCESS",
}


def connect_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    seed_db(conn)
    return conn


def seed_db(conn):
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            role TEXT,
            email TEXT,
            api_key TEXT
        );
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            amount INTEGER,
            card_hint TEXT
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price INTEGER
        );
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY,
            author TEXT,
            body TEXT
        );
        CREATE TABLE secrets (
            id INTEGER PRIMARY KEY,
            label TEXT,
            value TEXT
        );
        """
    )
    users = [
        (1, "alice", md5("alice123"), "user", "alice@example.test", "ak_live_alice_2025_demo"),
        (2, "bob", md5("bob123"), "user", "bob@example.test", "ak_live_bob_2025_demo"),
        (3, "admin", md5("admin123"), "admin", "admin@example.test", "ak_live_admin_2025_demo"),
    ]
    cur.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", users)
    cur.executemany(
        "INSERT INTO invoices VALUES (?, ?, ?, ?, ?)",
        [
            (1001, 1, "Alice cloud hosting", 120, "4111-1111-1111-1111"),
            (1002, 2, "Bob consulting", 840, "5555-2222-3333-4444"),
            (1003, 3, "Admin security tooling", 4300, "3782-822463-10005"),
        ],
    )
    cur.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        [
            (1, "Training VM", "lab", 99),
            (2, "Legacy CRM Connector", "plugin", 149),
            (3, "Debug Console License", "admin", 999),
            (4, "Internal Flag Product", "hidden", 0),
        ],
    )
    cur.execute("INSERT INTO comments(author, body) VALUES ('alice', 'Welcome to the demo board')")
    cur.executemany(
        "INSERT INTO secrets(label, value) VALUES (?, ?)",
        [
            ("access_control", FLAGS["A01"]),
            ("misconfiguration", FLAGS["A02"]),
            ("supply_chain", FLAGS["A03"]),
            ("crypto", FLAGS["A04"]),
            ("injection", FLAGS["A05"]),
        ],
    )
    conn.commit()


def md5(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()


DB = connect_db()


PAGES = [
    ("A01", "Broken Access Control", "/a01"),
    ("A02", "Security Misconfiguration", "/a02"),
    ("A03", "Software Supply Chain Failures", "/a03"),
    ("A04", "Cryptographic Failures", "/a04"),
    ("A05", "Injection", "/a05"),
]


FILES = {
    "public/readme.txt": "Public demo note. This one is safe to read.",
    "private/admin-api-key.txt": f"admin_api_key=super-secret-training-key\n{FLAGS['A02']}",
    "private/payroll.csv": "name,role,salary\nAlice,Engineer,120000\nBob,Manager,150000\nAdmin,CISO,250000\n",
}


DEPENDENCIES = [
    {
        "name": "jquery",
        "used": "1.8.3",
        "safe": "3.7.1",
        "risk": "Known vulnerable client library kept without a patch policy",
    },
    {
        "name": "left-pad-internal",
        "used": "0.0.2",
        "safe": "private registry only",
        "risk": "Package name is not scoped, allowing dependency confusion in the simulator",
    },
    {
        "name": "chart-lite",
        "used": "2.1.0",
        "safe": "2.1.0 + SRI",
        "risk": "Loaded from a CDN without integrity metadata",
    },
]


def page(title, body, status=HTTPStatus.OK):
    nav = "".join(
        f'<a class="nav-link" href="{href}">{code}</a>' for code, _name, href in PAGES
    )
    content = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | OWASP Top 10 2025 Lab</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #d7dee2;
      --panel: #f6f8f8;
      --accent: #0f766e;
      --warn: #b45309;
      --danger: #b91c1c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: #ffffff;
      line-height: 1.5;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: #eef6f4;
    }}
    .wrap {{
      width: min(1100px, calc(100% - 32px));
      margin: 0 auto;
    }}
    .top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 0;
    }}
    h1 {{ margin: 0; font-size: 28px; }}
    h2 {{ margin-top: 28px; font-size: 21px; }}
    h3 {{ margin-bottom: 8px; font-size: 17px; }}
    .subtitle {{ margin: 4px 0 0; color: var(--muted); }}
    nav {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .nav-link {{
      color: var(--ink);
      text-decoration: none;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 6px 10px;
      background: #fff;
    }}
    main {{ padding: 28px 0 48px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: #fff;
    }}
    .lab {{
      border-left: 4px solid var(--accent);
      background: var(--panel);
    }}
    .danger {{ color: var(--danger); font-weight: 700; }}
    .warn {{ color: var(--warn); font-weight: 700; }}
    form {{ display: grid; gap: 10px; margin: 10px 0; }}
    label {{ display: grid; gap: 4px; color: var(--muted); font-size: 14px; }}
    input, select, textarea {{
      width: 100%;
      border: 1px solid #b9c4ca;
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      background: #fff;
    }}
    button, .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: fit-content;
      border: 1px solid #0b5f59;
      border-radius: 6px;
      padding: 8px 12px;
      color: #fff;
      background: var(--accent);
      text-decoration: none;
      font: inherit;
      cursor: pointer;
    }}
    code, pre {{
      font-family: Consolas, Monaco, monospace;
      background: #eef1f2;
      border-radius: 6px;
    }}
    code {{ padding: 2px 5px; }}
    pre {{
      overflow: auto;
      padding: 12px;
      border: 1px solid var(--line);
      white-space: pre-wrap;
    }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px; text-align: left; }}
    .banner {{
      margin-top: 14px;
      padding: 10px 12px;
      border: 1px solid #f4c38a;
      border-radius: 8px;
      background: #fff7ed;
      color: #7c2d12;
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap top">
      <div>
        <h1><a href="/" style="color:inherit;text-decoration:none">OWASP Top 10 2025 Lab</a></h1>
        <p class="subtitle">로컬 테스트 전용 취약 웹사이트 모음</p>
      </div>
      <nav>{nav}</nav>
    </div>
  </header>
  <main class="wrap">
    <div class="banner"><strong>주의:</strong> 이 앱은 의도적으로 취약합니다. 인터넷에 노출하지 말고 127.0.0.1에서만 실행하세요.</div>
    {body}
  </main>
</body>
</html>"""
    return status, "text/html; charset=utf-8", content.encode("utf-8")


def card(title, description, inner):
    return f'<section class="card lab"><h3>{title}</h3><p>{description}</p>{inner}</section>'


def table(rows):
    if not rows:
        return "<p>No rows.</p>"
    headers = rows[0].keys()
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{html.escape(str(row[h]))}</td>" for h in headers) + "</tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


class LabHandler(BaseHTTPRequestHandler):
    server_version = "OWASPTop10Lab/2025"

    def do_GET(self):
        self.route()

    def do_POST(self):
        self.route()

    def route(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path == "/":
            self.respond(*home())
        elif path == "/a01":
            self.respond(*a01(qs))
        elif path == "/a02":
            self.respond(*a02(qs))
        elif path == "/a03":
            self.respond(*a03(qs))
        elif path == "/a04":
            self.respond(*a04(qs))
        elif path == "/a05":
            self.respond(*a05(self, qs))
        elif path == "/api/users":
            self.respond(*api_users())
        elif path == "/api/debug":
            self.respond(*api_debug())
        elif path.startswith("/download/"):
            self.respond(*download(path.removeprefix("/download/")))
        else:
            self.respond(*page("404", "<h2>Not found</h2>", HTTPStatus.NOT_FOUND))

    def form(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        return parse_qs(raw)

    def respond(self, status, content_type, payload):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Debug-Mode", "true")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


def home():
    cards = ""
    for code, name, href in PAGES:
        cards += f"""
        <article class="card">
          <h2>{code}:2025</h2>
          <p><strong>{name}</strong></p>
          <a class="button" href="{href}">Open lab</a>
        </article>
        """
    body = f"""
    <h2>Top 5 취약점별 테스트 사이트</h2>
    <p>각 메뉴에는 같은 취약점 범주를 보여주는 1~3개의 작은 실습 사이트가 들어 있습니다.</p>
    <div class="grid">{cards}</div>
    """
    return page("Home", body)


def a01(qs):
    user_id = qs.get("user_id", ["1"])[0]
    invoice_id = qs.get("invoice_id", ["1001"])[0]
    role = qs.get("role", ["user"])[0]
    profile = DB.execute(f"SELECT id, username, role, email, api_key FROM users WHERE id = {user_id}").fetchall()
    invoice = DB.execute(f"SELECT * FROM invoices WHERE id = {invoice_id}").fetchall()
    admin_panel = ""
    if role == "admin":
        users = DB.execute("SELECT id, username, role, email, api_key FROM users").fetchall()
        admin_panel = (
            "<h3>Admin Panel</h3>"
            "<p class='danger'>role parameter opens admin features.</p>"
            f"<pre>{FLAGS['A01']}</pre>"
            + table(users)
        )
    else:
        admin_panel = "<p>일반 사용자 화면입니다. URL의 <code>role</code> 값을 바꿔 보세요.</p>"
    body = f"""
    <h2>A01 Broken Access Control</h2>
    <div class="grid">
      {card("IDOR Profile", "세션 소유자 검증 없이 user_id 값으로 다른 사용자의 프로필을 조회합니다.", f'''
        <form method="get" action="/a01">
          <label>User ID <input name="user_id" value="{html.escape(user_id)}"></label>
          <button>조회</button>
        </form>
        {table(profile)}
      ''')}
      {card("IDOR Invoice", "청구서 소유자 확인 없이 invoice_id만 맞으면 민감 정보가 노출됩니다.", f'''
        <form method="get" action="/a01">
          <label>Invoice ID <input name="invoice_id" value="{html.escape(invoice_id)}"></label>
          <button>조회</button>
        </form>
        {table(invoice)}
      ''')}
      {card("Role Parameter Bypass", "권한을 서버 세션이 아니라 사용자가 보낸 role 파라미터로 판단합니다.", f'''
        <p>현재 role: <code>{html.escape(role)}</code></p>
        <p><a href="/a01?role=admin">/a01?role=admin</a></p>
        {admin_panel}
      ''')}
    </div>
    """
    return page("A01 Broken Access Control", body)


def a02(qs):
    file_name = unquote(qs.get("file", ["public/readme.txt"])[0])
    listing = "".join(f"<li><a href='/download/{quote(name)}'>{html.escape(name)}</a></li>" for name in FILES)
    body = f"""
    <h2>A02 Security Misconfiguration</h2>
    <div class="grid">
      {card("Debug Endpoint", "운영 설정처럼 보이는 디버그 정보와 환경 변수를 노출합니다.", '''
        <p><a class="button" href="/api/debug">/api/debug</a></p>
        <p>응답 헤더에도 <code>X-Debug-Mode: true</code>가 붙습니다.</p>
      ''')}
      {card("Open Directory Listing", "파일 목록을 사용자에게 그대로 보여주고 private 경로까지 노출합니다.", f'''
        <ul>{listing}</ul>
      ''')}
      {card("Over-Permissive CORS", "모든 응답에 Access-Control-Allow-Origin: * 를 붙입니다.", '''
        <pre>Access-Control-Allow-Origin: *
X-Debug-Mode: true</pre>
      ''')}
    </div>
    <h3>File preview</h3>
    <form method="get" action="/a02">
      <label>File path <input name="file" value="{html.escape(file_name)}"></label>
      <button>읽기</button>
    </form>
    <pre>{html.escape(FILES.get(file_name, "No such demo file"))}</pre>
    """
    return page("A02 Security Misconfiguration", body)


def a03(qs):
    pkg = qs.get("package", ["left-pad-internal"])[0]
    source = qs.get("source", ["public-registry"])[0]
    install_result = "Internal package resolved safely."
    if pkg == "left-pad-internal" and source == "public-registry":
        install_result = (
            "WARNING: public-registry/left-pad-internal@9.9.9 wins over the intended private package.\n"
            f"{FLAGS['A03']}"
        )
    dep_rows = [
        {"name": d["name"], "used": d["used"], "recommended": d["safe"], "risk": d["risk"]}
        for d in DEPENDENCIES
    ]
    body = f"""
    <h2>A03 Software Supply Chain Failures</h2>
    <div class="grid">
      {card("Known Vulnerable Components", "취약하거나 오래된 컴포넌트를 추적 없이 유지하는 상황을 보여줍니다.", table(dep_rows))}
      {card("Dependency Confusion Simulator", "내부 패키지 이름이 public registry에서 먼저 해석되는 설정입니다.", f'''
        <form method="get" action="/a03">
          <label>Package <input name="package" value="{html.escape(pkg)}"></label>
          <label>Source
            <select name="source">
              <option value="public-registry">public-registry</option>
              <option value="private-registry">private-registry</option>
            </select>
          </label>
          <button>Resolve</button>
        </form>
        <pre>{html.escape(install_result)}</pre>
      ''')}
      {card("Missing SRI", "외부 스크립트를 무결성 검증 없이 로드하는 HTML 조각입니다.", '''
        <pre>&lt;script src="https://cdn.example.test/chart-lite/2.1.0/chart.js"&gt;&lt;/script&gt;</pre>
      ''')}
    </div>
    """
    return page("A03 Software Supply Chain Failures", body)


def a04(qs):
    token_user = qs.get("token_user", ["alice"])[0]
    reset_id = qs.get("reset_id", ["1"])[0]
    token_role = "admin" if token_user == "admin" else "user"
    token_payload = f"user={token_user}&role={token_role}"
    if token_user == "admin":
        token_payload += f"&flag={FLAGS['A04']}"
    encoded = base64.urlsafe_b64encode(token_payload.encode()).decode()
    reset_token = hashlib.md5(f"{reset_id}:{int(time.time() // 3600)}".encode()).hexdigest()[:10]
    users = DB.execute("SELECT username, password, email FROM users").fetchall()
    body = f"""
    <h2>A04 Cryptographic Failures</h2>
    <div class="grid">
      {card("Weak Password Hashes", "비밀번호를 빠르게 대입 가능한 MD5 해시로 저장합니다.", table(users))}
      {card("Encoded Token Mistaken for Encryption", "Base64 인코딩 값을 암호화로 오해해 역할 정보를 그대로 담습니다.", f'''
        <form method="get" action="/a04">
          <label>User <input name="token_user" value="{html.escape(token_user)}"></label>
          <button>토큰 발급</button>
        </form>
        <pre>{html.escape(encoded)}</pre>
        <p>Decode: <code>{html.escape(base64.urlsafe_b64decode(encoded).decode())}</code></p>
      ''')}
      {card("Predictable Reset Token", "사용자 ID와 현재 시간대만으로 재설정 토큰을 만들기 때문에 예측 가능합니다.", f'''
        <form method="get" action="/a04">
          <label>User ID <input name="reset_id" value="{html.escape(reset_id)}"></label>
          <button>토큰 생성</button>
        </form>
        <pre>{html.escape(reset_token)}</pre>
      ''')}
    </div>
    """
    return page("A04 Cryptographic Failures", body)


def a05(handler, qs):
    message = ""
    search = qs.get("q", ["lab"])[0]
    rows = []
    sql = f"SELECT id, name, category, price FROM products WHERE name LIKE '%{search}%' OR category LIKE '%{search}%'"
    try:
        rows = DB.execute(sql).fetchall()
        if "' OR '1'='1" in search or "UNION" in search.upper():
            message = FLAGS["A05"]
    except sqlite3.Error as exc:
        message = f"SQL error: {exc}"

    if handler.command == "POST":
        form = handler.form()
        author = form.get("author", ["anonymous"])[0]
        body = form.get("body", [""])[0]
        DB.execute(f"INSERT INTO comments(author, body) VALUES ('{author}', '{body}')")
        DB.commit()
        message = "Comment saved."

    name = qs.get("name", ["<script>alert('xss')</script>"])[0]
    comments = DB.execute("SELECT author, body FROM comments ORDER BY id DESC LIMIT 5").fetchall()
    rendered_comments = "".join(
        f"<p><strong>{row['author']}</strong>: {row['body']}</p>" for row in comments
    )
    body = f"""
    <h2>A05 Injection</h2>
    <div class="grid">
      {card("SQL Injection Search", "검색어를 SQL 문자열에 직접 붙여 쿼리를 실행합니다.", f'''
        <form method="get" action="/a05">
          <label>Search <input name="q" value="{html.escape(search)}"></label>
          <button>검색</button>
        </form>
        <pre>{html.escape(sql)}</pre>
        <p class="warn">{html.escape(message)}</p>
        {table(rows)}
      ''')}
      {card("Reflected XSS", "입력값을 HTML 이스케이프 없이 응답에 반사합니다.", f'''
        <form method="get" action="/a05">
          <label>Name <input name="name" value="{html.escape(name)}"></label>
          <button>반영</button>
        </form>
        <p>Hello, {name}</p>
      ''')}
      {card("Stored XSS", "게시판 입력을 저장한 뒤 이스케이프 없이 렌더링합니다.", f'''
        <form method="post" action="/a05">
          <label>Author <input name="author" value="tester"></label>
          <label>Comment <textarea name="body">&lt;img src=x onerror=alert('stored')&gt;</textarea></label>
          <button>저장</button>
        </form>
        <div>{rendered_comments}</div>
      ''')}
    </div>
    """
    return page("A05 Injection", body)


def api_users():
    users = DB.execute("SELECT id, username, role, email, api_key FROM users").fetchall()
    payload = json.dumps([dict(row) for row in users], indent=2).encode("utf-8")
    return HTTPStatus.OK, "application/json; charset=utf-8", payload


def api_debug():
    payload = {
        "debug": True,
        "database": "sqlite://:memory:",
        "server": "ThreadingHTTPServer",
        "example_env": {
            "APP_ENV": os.environ.get("APP_ENV", "production"),
            "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-secret-key-leaked"),
        },
        "users_endpoint": "/api/users",
    }
    return HTTPStatus.OK, "application/json; charset=utf-8", json.dumps(payload, indent=2).encode("utf-8")


def download(name):
    name = unquote(name)
    if name in FILES:
        return HTTPStatus.OK, "text/plain; charset=utf-8", FILES[name].encode("utf-8")
    return HTTPStatus.NOT_FOUND, "text/plain; charset=utf-8", b"No such demo file"


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), LabHandler)
    print(f"OWASP Top 10 2025 vulnerable lab running at http://{HOST}:{PORT}")
    print("Do not expose this intentionally vulnerable app to a network.")
    server.serve_forever()
