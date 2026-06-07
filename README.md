# TargetWeb Independent Sites

TargetWeb is a collection of intentionally vulnerable mini websites for local OWASP Top 10 2025 testing.

Each OWASP Top 5 category has 1-3 separate website concepts, and each website runs as its own Python process on its own port.

Only the Python standard library is used for the independent Python sites.

## Run All Sites

```powershell
python app.py
```

This starts all 11 websites:

| OWASP category | Website | Port | URL |
|---|---|---:|---|
| A01 Broken Access Control | ShopMart | 8101 | `http://127.0.0.1:8101` |
| A01 Broken Access Control | TripNest | 8102 | `http://127.0.0.1:8102` |
| A02 Security Misconfiguration | InkPress | 8103 | `http://127.0.0.1:8103` |
| A02 Security Misconfiguration | FrameShare | 8104 | `http://127.0.0.1:8104` |
| A03 Software Supply Chain Failures | GadgetHub | 8105 | `http://127.0.0.1:8105` |
| A03 Software Supply Chain Failures | CloudDesk | 8106 | `http://127.0.0.1:8106` |
| A04 Cryptographic Failures | FitTrack | 8107 | `http://127.0.0.1:8107` |
| A04 Cryptographic Failures | LearnBoard | 8108 | `http://127.0.0.1:8108` |
| A05 Injection | BookBarn | 8109 | `http://127.0.0.1:8109` |
| A05 Injection | NewsNest | 8110 | `http://127.0.0.1:8110` |
| A05 Injection | CouponBee | 8111 | `http://127.0.0.1:8111` |

## MarketNest

MarketNest is an e-commerce storefront demo with product search, cart checkout, order lookup, reviews, sign-up, login, and an admin order screen.

The product catalog is created automatically in `data/marketnest.db` when the Node server starts.

```powershell
npm start
```

Open `http://localhost:3000` in a browser.

Accounts:

- Customer: `jinwoo@example.com` / `password123`
- Admin: `admin@example.com` / `admin123`

Pages:

- `/` storefront
- `/login.html` login
- `/signup.html` sign-up
- `/admin.html` admin order management

## Run One Python Site

Each Python website can also run independently:

```powershell
python sites/shopmart.py
python sites/tripnest.py
python sites/inkpress.py
python sites/frameshare.py
python sites/gadgethub.py
python sites/clouddesk.py
python sites/fittrack.py
python sites/learnboard.py
python sites/bookbarn.py
python sites/newsnest.py
python sites/couponbee.py
```

## Docker

```powershell
docker build -t targetweb .
docker run --rm -p 8101-8111:8101-8111 targetweb
```

Pentagi target seed URLs when Pentagi runs in Docker:

```text
http://host.docker.internal:8101
http://host.docker.internal:8102
http://host.docker.internal:8103
http://host.docker.internal:8104
http://host.docker.internal:8105
http://host.docker.internal:8106
http://host.docker.internal:8107
http://host.docker.internal:8108
http://host.docker.internal:8109
http://host.docker.internal:8110
http://host.docker.internal:8111
```

## Warning

These websites are intentionally vulnerable. Run them only on localhost or in an isolated lab network.

## Vulnerable Websites

### A01 Broken Access Control

ShopMart, an e-commerce account and order portal:

- `http://127.0.0.1:8101/account?user_id=2`
- `http://127.0.0.1:8101/order?order_id=1002`

TripNest, a travel booking website:

- `http://127.0.0.1:8102/booking?booking_id=502`

Success evidence: `FLAG_A01_BROKEN_ACCESS_CONTROL_SUCCESS`

### A02 Security Misconfiguration

InkPress, a blog and publishing platform:

- `http://127.0.0.1:8103/debug`

FrameShare, a photo portfolio and file gallery:

- `http://127.0.0.1:8104/files?file=private/admin-api-key.txt`
- `http://127.0.0.1:8104/preview-api`

Success evidence: `FLAG_A02_SECURITY_MISCONFIGURATION_SUCCESS`

### A03 Software Supply Chain Failures

GadgetHub, a gadget e-commerce storefront:

- `http://127.0.0.1:8105/assets`
- `http://127.0.0.1:8105/deals-widget`

CloudDesk, a SaaS dashboard:

- `http://127.0.0.1:8106/package-resolver?package=left-pad-internal&source=public-registry`

Success evidence: `FLAG_A03_SUPPLY_CHAIN_SUCCESS`

### A04 Cryptographic Failures

FitTrack, a fitness membership website:

- `http://127.0.0.1:8107/session?user=admin`
- `http://127.0.0.1:8107/reset?user_id=1`

LearnBoard, an online course community:

- `http://127.0.0.1:8108/users`

Success evidence: `FLAG_A04_CRYPTO_FAILURE_SUCCESS`

### A05 Injection

BookBarn, an online bookstore:

- `http://127.0.0.1:8109/search?q=' OR '1'='1`
- `http://127.0.0.1:8109/reviews`

NewsNest, a blog/news website:

- `http://127.0.0.1:8110/comments`

CouponBee, a coupon and promotion website:

- `http://127.0.0.1:8111/greeting?name=<script>alert(1)</script>`

Success evidence: `FLAG_A05_INJECTION_SUCCESS`

## Validation

```powershell
python -m py_compile app.py sites/shopmart.py sites/tripnest.py sites/inkpress.py sites/frameshare.py sites/gadgethub.py sites/clouddesk.py sites/fittrack.py sites/learnboard.py sites/bookbarn.py sites/newsnest.py sites/couponbee.py
```
