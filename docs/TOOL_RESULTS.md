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
| Runtime Docker | Compose no GitHub Actions | balanceamento e smoke test aprovados |

O Vite informou que o bundle principal é maior que 500 kB. É uma oportunidade de otimização, não um erro de build.

## Segurança automatizada

| Ferramenta | Escopo | Resultado local |
|---|---|---|
| Bandit 1.8.3 | backend, excluindo testes | nenhuma ocorrência após correções |
| pip-audit 2.8.0 | `backend/requirements.txt` | nenhuma vulnerabilidade conhecida |
| npm audit | `frontend/package-lock.json` | etapa concluída no CI |
| Gitleaks | histórico Git | nenhuma exposição detectada no CI |

O primeiro uso do Bandit sinalizou consultas SQL interpoladas no blueprint inativo, `assert` usado como validação e bind de desenvolvimento em todas as interfaces. Esses pontos foram corrigidos antes da execução final.

## Infraestrutura

Docker não estava disponível no ambiente local. A validação de runtime foi executada no GitHub Actions:

- `docker compose config` validou a configuração;
- as imagens de backend e frontend foram construídas;
- Nginx, frontend e duas réplicas do backend foram iniciados;
- oito requisições alcançaram `backend-1` e `backend-2`;
- o smoke test confirmou HTTP 401 sem token e headers de segurança ativos;
- os containers foram encerrados e os volumes temporários removidos.

Saída sanitizada: [evidência de balanceamento](evidence/LOAD-BALANCING.md).

Nenhum resultado de ferramenta foi inventado ou marcado como aprovado sem execução.
