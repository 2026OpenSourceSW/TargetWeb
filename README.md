# OWASP Top 10 2025 Vulnerable Lab

OWASP Top 10 2025 기준 Top 5 항목을 로컬에서 테스트할 수 있는 의도적 취약 웹사이트 모음입니다.

공식 OWASP Top 10 2025 Top 5:

1. A01:2025 Broken Access Control
2. A02:2025 Security Misconfiguration
3. A03:2025 Software Supply Chain Failures
4. A04:2025 Cryptographic Failures
5. A05:2025 Injection

## 실행

Python 표준 라이브러리만 사용합니다.

```powershell
python app.py
```

브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:8000
```

## Pentagi에서 사용

로컬에서 Pentagi가 실행된다면 target URL에 다음 값을 넣으면 됩니다.

```text
http://127.0.0.1:8000
```

Pentagi가 Docker 컨테이너에서 실행된다면 이 앱도 Docker로 띄우는 방식이 가장 단순합니다.

```powershell
docker build -t owasp-top10-2025-lab .
docker run --rm -p 8000:8000 owasp-top10-2025-lab
```

그 다음 Pentagi target URL:

```text
http://host.docker.internal:8000
```

각 취약점은 exploit 성공 증거로 `FLAG_A01`부터 `FLAG_A05`까지의 문자열을 응답에 노출합니다.

포트를 바꾸려면:

```powershell
$env:OWASP_LAB_PORT=8080
python app.py
```

## 주의

이 앱은 교육과 테스트를 위해 의도적으로 취약하게 만들어졌습니다. `127.0.0.1`에서만 실행하고 외부 네트워크에 노출하지 마세요.

## 포함된 취약점

### A01 Broken Access Control

- IDOR Profile: `/a01?user_id=2`
- IDOR Invoice: `/a01?invoice_id=1002`
- Role Parameter Bypass: `/a01?role=admin`

### A02 Security Misconfiguration

- Debug Endpoint: `/api/debug`
- Open Directory Listing: `/a02`
- Over-Permissive CORS: 모든 응답에 `Access-Control-Allow-Origin: *`

### A03 Software Supply Chain Failures

- Known Vulnerable Components 목록
- Dependency Confusion Simulator
- Missing Subresource Integrity 예시

### A04 Cryptographic Failures

- Weak Password Hashes: MD5 저장
- Encoded Token Mistaken for Encryption: Base64 토큰
- Predictable Reset Token: 예측 가능한 재설정 토큰

### A05 Injection

- SQL Injection Search: `/a05?q=' OR '1'='1`
- Reflected XSS: `/a05?name=<script>alert('xss')</script>`
- Stored XSS: 게시판 입력값을 이스케이프 없이 저장/렌더링

## 참고

OWASP 공식 문서: <https://owasp.org/Top10/2025/en/>
