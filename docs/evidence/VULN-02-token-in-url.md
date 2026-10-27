# VULN-02 — Token transmitido na URL

## Antes da correção

Baseline: `f0765ae1f97a48d19f25b37debc033fe4bd5160f`

O frontend construía a requisição abaixo:

```http
GET /users/info?id_token=TEST_TOKEN_NOT_A_SECRET HTTP/1.1
Host: 127.0.0.1:5000
```

O backend lia o valor com `request.args.get("id_token")`. Foi utilizado somente um texto fictício para registrar o formato.

## Depois da correção

```http
GET /users/info HTTP/1.1
Authorization: Bearer TEST_TOKEN_NOT_A_SECRET
```

Uma tentativa de manter o token na URL sem o header é rejeitada:

```http
HTTP/1.1 401 UNAUTHORIZED
Content-Type: application/json

{"error":{"code":"authentication_required","message":"A valid bearer token is required."}}
```

Teste automatizado: `test_token_in_query_string_is_not_accepted`.
