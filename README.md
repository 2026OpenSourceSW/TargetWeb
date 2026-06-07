# MarketNest

MarketNest는 전자상거래 쇼핑몰 컨셉의 웹사이트입니다. 상품 검색, 장바구니, 결제, 주문 조회, 리뷰, 회원가입, 로그인, 관리자 주문 관리 화면을 포함합니다.

서버는 Python 표준 라이브러리로 실행되며, 상품 카탈로그는 `data/marketnest.db` SQLite 데이터베이스에서 로드됩니다.

## 실행

```powershell
python app.py
```

브라우저에서 `http://localhost:3010`을 엽니다.

## 계정

- 일반 회원: `jinwoo@example.com` / `password123`
- 관리자: `admin@example.com` / `admin123`

## 주요 화면

- `/` 스토어 메인
- `/login.html` 로그인
- `/signup.html` 회원가입
- `/admin.html` 관리자 주문 관리

## 주요 기능

- 상품 검색 및 상품 목록 조회
- 장바구니 담기
- 쿠폰 할인율 입력과 결제 요청
- 회원 번호 기반 주문 조회
- 상품 리뷰 등록 및 조회
- 관리자 주문 목록 확인

## 프로젝트 구조

```text
.
|-- app.py
|-- data/
|   `-- marketnest.db
|-- public/
|   |-- admin.html
|   |-- admin.js
|   |-- app.js
|   |-- auth.js
|   |-- index.html
|   |-- login.html
|   |-- login.js
|   |-- signup.html
|   |-- signup.js
|   `-- styles.css
`-- README.md
```
