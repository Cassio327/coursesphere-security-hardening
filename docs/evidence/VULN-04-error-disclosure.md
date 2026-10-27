# VULN-04 — Exposição de erro interno

## Antes da correção

Baseline: `f0765ae1f97a48d19f25b37debc033fe4bd5160f`

```http
POST /users/create HTTP/1.1
Content-Type: application/json

{"email":"candidate@example.com","password":"long-password"}
```

Trecho sanitizado da resposta local:

```http
HTTP/1.1 400 BAD REQUEST

{"error":"Error creating user: ... FIREBASE_CREDENTIALS_PATH and FIREBASE_DATABASE_URL ..."}
```

A resposta revelou detalhes de configuração que deveriam permanecer apenas nos logs internos.

## Depois da correção

```http
HTTP/1.1 503 SERVICE UNAVAILABLE
Content-Type: application/json

{"error":{"code":"identity_service_unavailable","message":"The identity service is temporarily unavailable."}}
```

O teste `test_internal_exception_is_not_exposed` injeta um caminho sensível fictício e confirma que ele não aparece no corpo da resposta.
