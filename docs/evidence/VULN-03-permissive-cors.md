# VULN-03 — CORS permissivo

## Antes da correção

Baseline: `f0765ae1f97a48d19f25b37debc033fe4bd5160f`

```http
GET /users/info HTTP/1.1
Origin: https://attacker.example
```

Resposta observada com a configuração global `CORS(app)`:

```http
Access-Control-Allow-Origin: https://attacker.example
Vary: Origin
```

## Depois da correção

As origens são definidas por `CORS_ALLOWED_ORIGINS`. Para uma origem não configurada, a resposta não contém `Access-Control-Allow-Origin`.

```http
GET /health HTTP/1.1
Origin: https://attacker.example
```

Resultado verificado: header CORS ausente. Para `http://localhost:8080`, o header é retornado com essa origem exata.

Teste automatizado: `test_cors_allows_only_configured_origin`.
