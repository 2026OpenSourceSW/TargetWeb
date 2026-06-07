const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { DatabaseSync } = require("node:sqlite");

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, "public");
const DATA_DIR = path.join(__dirname, "data");
const DB_PATH = path.join(DATA_DIR, "marketnest.db");

const users = [
  {
    id: 1,
    role: "customer",
    name: "Jin Woo",
    email: "jinwoo@example.com",
    password: "password123",
    apiKey: "cust_live_plaintext_7f4d2b",
    cardNumber: "4111111111111111",
    cvv: "123"
  },
  {
    id: 2,
    role: "admin",
    name: "Admin Mina",
    email: "admin@example.com",
    password: "admin123",
    apiKey: "admin_live_plaintext_99a81c",
    cardNumber: "5555555555554444",
    cvv: "999"
  }
];

const products = [
  {
    id: 101,
    name: "Nimbus Sneakers",
    category: "shoes",
    price: 89000,
    image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
    description: "Lightweight knit sneakers for daily city walking."
  },
  {
    id: 102,
    name: "Aurora Headphones",
    category: "electronics",
    price: 129000,
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
    description: "Wireless over-ear headphones with rich bass."
  },
  {
    id: 103,
    name: "Canvas Weekender",
    category: "bags",
    price: 72000,
    image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
    description: "Compact travel bag with laptop sleeve."
  },
  {
    id: 104,
    name: "Ceramic Pour-over Set",
    category: "home",
    price: 54000,
    image: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
    description: "Slow coffee kit for a clean morning brew."
  },
  {
    id: 105,
    name: "Metro Smartwatch",
    category: "electronics",
    price: 174000,
    image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
    description: "Activity tracking and notification companion."
  },
  {
    id: 106,
    name: "Linen Overshirt",
    category: "fashion",
    price: 63000,
    image: "https://images.unsplash.com/photo-1520975954732-35dd22299614?auto=format&fit=crop&w=900&q=80",
    description: "Breathable overshirt for layered outfits."
  }
];

const orders = [
  { id: 9001, userId: 1, total: 218000, status: "paid", items: ["Nimbus Sneakers", "Aurora Headphones"] },
  { id: 9002, userId: 2, total: 54000, status: "internal-review", items: ["Ceramic Pour-over Set"] }
];

const reviews = [
  { productId: 101, author: "soyeon", body: "Comfortable enough for a full day out." },
  { productId: 102, author: "minjae", body: "Battery lasts longer than expected." }
];

const sessions = new Map();
let db;

function initializeDatabase() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  db = new DatabaseSync(DB_PATH);
  db.exec(`
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
  `);

  const insertProduct = db.prepare(`
    INSERT INTO products (id, name, category, price, image, description)
    VALUES (?, ?, ?, ?, ?, ?)
  `);

  for (const product of products) {
    insertProduct.run(
      product.id,
      product.name,
      product.category,
      product.price,
      product.image,
      product.description
    );
  }

  const insertNote = db.prepare("INSERT INTO customer_private_notes (id, email, memo) VALUES (?, ?, ?)");
  insertNote.run(1, "jinwoo@example.com", "VIP coupon code: NEST-VIP-70");
  insertNote.run(2, "admin@example.com", "Back-office approval memo: refund manually");
}

initializeDatabase();

function sendJson(res, statusCode, payload, headers = {}) {
  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "X-Powered-By": "MarketNest/1.0",
    ...headers
  });
  res.end(JSON.stringify(payload, null, 2));
}

function sendText(res, statusCode, payload) {
  res.writeHead(statusCode, { "Content-Type": "text/plain; charset=utf-8" });
  res.end(payload);
}

function readBody(req) {
  return new Promise((resolve) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
    });
    req.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        resolve({ malformedBody: body, parseError: error.message });
      }
    });
  });
}

function getSession(req) {
  const cookie = req.headers.cookie || "";
  const match = cookie.match(/session=([^;]+)/);
  if (!match) return null;
  return sessions.get(match[1]) || null;
}

function serveStatic(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const requestedPath = url.pathname === "/" ? "/index.html" : url.pathname;
  const filePath = path.normalize(path.join(PUBLIC_DIR, requestedPath));

  if (!filePath.startsWith(PUBLIC_DIR)) {
    return sendText(res, 403, "Forbidden");
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      return sendText(res, 404, "Not found");
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentTypes = {
      ".html": "text/html; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".js": "application/javascript; charset=utf-8"
    };
    res.writeHead(200, { "Content-Type": contentTypes[ext] || "application/octet-stream" });
    res.end(data);
  });
}

function searchCatalog(query) {
  const simulatedSql = `SELECT * FROM products WHERE name LIKE '%${query}%' OR category LIKE '%${query}%'`;

  try {
    return {
      simulatedSql,
      results: db.prepare(simulatedSql).all()
    };
  } catch (error) {
    return {
      simulatedSql,
      results: [],
      databaseError: error.message
    };
  }
}

function listProducts() {
  return db.prepare("SELECT * FROM products ORDER BY id").all();
}

async function handleApi(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const session = getSession(req);

  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    });
    return res.end();
  }

  try {
    if (req.method === "POST" && url.pathname === "/api/login") {
      const body = await readBody(req);
      const user = users.find((candidate) => candidate.email === body.email && candidate.password === body.password);
      if (!user) return sendJson(res, 401, { error: "Invalid email or password" });

      const token = Buffer.from(`${user.id}:${Date.now()}`).toString("base64");
      sessions.set(token, { id: user.id, role: user.role, name: user.name, email: user.email });

      res.writeHead(200, {
        "Content-Type": "application/json; charset=utf-8",
        "Set-Cookie": `session=${token}; Path=/`,
        "Access-Control-Allow-Origin": "*"
      });
      return res.end(JSON.stringify({ user: sessions.get(token) }, null, 2));
    }

    if (req.method === "POST" && url.pathname === "/api/signup") {
      const body = await readBody(req);
      if (!body.name || !body.email || !body.password) {
        return sendJson(res, 400, { error: "Name, email, and password are required." });
      }

      if (users.some((candidate) => candidate.email === body.email)) {
        return sendJson(res, 409, { error: "Email already exists." });
      }

      const user = {
        id: users.length + 1,
        role: "customer",
        name: body.name,
        email: body.email,
        password: body.password,
        apiKey: `cust_live_plaintext_${crypto.randomBytes(3).toString("hex")}`,
        cardNumber: body.cardNumber || "4000000000000002",
        cvv: body.cvv || "000"
      };
      users.push(user);

      const token = Buffer.from(`${user.id}:${Date.now()}`).toString("base64");
      sessions.set(token, { id: user.id, role: user.role, name: user.name, email: user.email });

      res.writeHead(201, {
        "Content-Type": "application/json; charset=utf-8",
        "Set-Cookie": `session=${token}; Path=/`,
        "Access-Control-Allow-Origin": "*"
      });
      return res.end(JSON.stringify({ user: sessions.get(token) }, null, 2));
    }

    if (req.method === "POST" && url.pathname === "/api/logout") {
      const cookie = req.headers.cookie || "";
      const match = cookie.match(/session=([^;]+)/);
      if (match) sessions.delete(match[1]);
      res.writeHead(200, {
        "Content-Type": "application/json; charset=utf-8",
        "Set-Cookie": "session=; Path=/; Max-Age=0",
        "Access-Control-Allow-Origin": "*"
      });
      return res.end(JSON.stringify({ ok: true }, null, 2));
    }

    if (url.pathname === "/api/me") {
      return sendJson(res, 200, { user: session || null });
    }

    if (url.pathname === "/api/products") {
      return sendJson(res, 200, { products: listProducts() });
    }

    if (url.pathname === "/api/search") {
      return sendJson(res, 200, searchCatalog(url.searchParams.get("q") || ""));
    }

    if (url.pathname === "/api/reviews" && req.method === "GET") {
      const productId = Number(url.searchParams.get("productId"));
      return sendJson(res, 200, { reviews: reviews.filter((review) => review.productId === productId) });
    }

    if (url.pathname === "/api/reviews" && req.method === "POST") {
      const body = await readBody(req);
      const review = {
        productId: Number(body.productId),
        author: body.author || "anonymous",
        body: body.body || ""
      };
      reviews.push(review);
      return sendJson(res, 201, { review });
    }

    if (url.pathname === "/api/orders") {
      const userId = Number(url.searchParams.get("userId") || (session && session.id) || 1);
      return sendJson(res, 200, {
        orders: orders.filter((order) => order.userId === userId)
      });
    }

    if (url.pathname === "/api/admin/orders") {
      return sendJson(res, 200, {
        orders,
        currentUser: session
      });
    }

    if (url.pathname === "/api/checkout" && req.method === "POST") {
      const body = await readBody(req);
      const clientTotal = Number(body.clientTotal || 0);
      const discountPercent = Number(body.discountPercent || 0);
      const finalTotal = Math.round(clientTotal * (1 - discountPercent / 100));
      const order = {
        id: crypto.randomInt(10000, 99999),
        userId: session ? session.id : 1,
        total: finalTotal,
        status: "paid",
        items: body.items || []
      };
      orders.push(order);

      return sendJson(res, 201, {
        order
      });
    }

    if (url.pathname === "/api/internal/customer") {
      return sendJson(res, 200, {
        customers: users.map((user) => ({
          id: user.id,
          email: user.email,
          password: user.password,
          apiKey: user.apiKey,
          cardNumber: user.cardNumber,
          cvv: user.cvv
        }))
      });
    }

    if (url.pathname === "/api/internal/env") {
      return sendJson(res, 200, {
        nodeVersion: process.version,
        platform: process.platform,
        cwd: process.cwd(),
        envSample: {
          NODE_ENV: process.env.NODE_ENV || "development",
          PORT,
          SECRET_KEY: "dev-secret-key-checked-into-demo"
        },
        headers: req.headers
      });
    }

    if (url.pathname === "/api/error") {
      throw new Error("Unexpected catalog service failure.");
    }

    return sendJson(res, 404, { error: "API route not found" });
  } catch (error) {
    return sendJson(res, 500, {
      error: error.message,
      stack: error.stack
    });
  }
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith("/api/")) {
    return handleApi(req, res);
  }

  return serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`MarketNest running at http://localhost:${PORT}`);
});
