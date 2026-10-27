# Resultados das validações

Data: 27/10/2026.

## Testes e build

| Verificação | Comando | Resultado |
|---|---|---|
| Testes backend | `pytest -q backend/tests` | 10 aprovados |
| Compilação Python | `python -m compileall -q backend` | concluída |
| Lint frontend | `npm run lint` | concluído sem erros |
| Build frontend | `npm run build` | concluído |
| YAML e dashboard | parsing com PyYAML e JSON | válidos |
| Scripts shell | `sh -n scripts/*.sh` | sintaxe válida |

O Vite informou que o bundle principal é maior que 500 kB. É uma oportunidade de otimização, não um erro de build.

## Segurança automatizada

| Ferramenta | Escopo | Resultado local |
|---|---|---|
| Bandit 1.8.3 | backend, excluindo testes | nenhuma ocorrência após correções |
| pip-audit 2.8.0 | `backend/requirements.txt` | nenhuma vulnerabilidade conhecida |
| npm audit | `frontend/package-lock.json` | execução local inconclusiva por timeout de rede; executada no CI |
| Gitleaks | histórico Git | configurado no CI |

O primeiro uso do Bandit sinalizou consultas SQL interpoladas no blueprint inativo, `assert` usado como validação e bind de desenvolvimento em todas as interfaces. Esses pontos foram corrigidos antes da execução final.

## Infraestrutura

Docker não estava disponível no ambiente usado para esta rodada local. Por isso:

- os arquivos Compose, Prometheus e Grafana foram validados sintaticamente;
- os Dockerfiles foram incluídos na revisão manual;
- o pipeline executa `docker compose config` e constrói as imagens;
- a demonstração final em host com Docker deve executar `make up`, `make load-balance` e `make smoke`.

Nenhum resultado de ferramenta foi inventado ou marcado como aprovado sem execução.
