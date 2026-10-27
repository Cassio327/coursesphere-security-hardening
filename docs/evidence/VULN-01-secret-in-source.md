# VULN-01 — Credencial no código-fonte

## Evidência sanitizada

- Origem: repositório de referência `LambdaAK/CourseSphere`
- Commit analisado: `71616a08b8756f048d5bf237be433c3b996a43d1`
- Caminho observado: `backend/cornell-course-sphere-data/reddit-data/reddit_key.json`
- Nomes de campos observados: `client_id` e `client_secret`

Os valores não foram copiados, testados ou incluídos em logs. O arquivo foi removido antes da primeira publicação deste repositório.

## Verificação da mitigação

```bash
git ls-files | grep -E 'reddit_key|credentials\.json|\.env$'
```

Resultado esperado: nenhuma ocorrência. O pipeline também executa Gitleaks sobre o histórico.

## Limite

A remoção da cópia não invalida o segredo exposto no repositório original. A revogação depende do proprietário da integração.
