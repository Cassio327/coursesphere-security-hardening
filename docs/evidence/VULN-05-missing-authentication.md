# VULN-05 — Consulta sem autenticação

## Antes da correção

Baseline: `f0765ae1f97a48d19f25b37debc033fe4bd5160f`

```http
POST /users/query HTTP/1.1
Content-Type: application/json

{"query":"show my courses"}
```

Resposta observada no ambiente local:

```http
HTTP/1.1 200 OK
Content-Type: application/json

"Fake implementation"
```

Nenhum token era necessário para alcançar o processamento.

## Depois da correção

A mesma requisição retorna:

```http
HTTP/1.1 401 UNAUTHORIZED
Content-Type: application/json

{"error":{"code":"authentication_required","message":"A valid bearer token is required."}}
```

Com Bearer token válido, a rota associa a operação ao `uid` verificado antes de carregar o perfil. Testes automatizados: `test_protected_query_rejects_missing_token` e `test_valid_bearer_token_allows_query`.
