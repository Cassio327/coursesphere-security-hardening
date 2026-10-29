# Resultados das validações

Data da validação final: 29/10/2026.

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

O Vite informou que o bundle principal é maior que 500 kB. O build permanece válido;
a divisão de código é uma oportunidade de desempenho, não uma falha de segurança.

## Segurança automatizada

| Ferramenta | Escopo | Resultado final |
|---|---|---|
| Bandit 1.8.3 | backend, excluindo testes | nenhuma ocorrência |
| pip-audit 2.8.0 | `backend/requirements.txt` | nenhuma vulnerabilidade conhecida |
| npm audit | `frontend/package-lock.json` | 0 vulnerabilidades conhecidas |
| Gitleaks | histórico Git | nenhuma exposição detectada no CI |

O primeiro uso do Bandit sinalizou consultas SQL interpoladas no blueprint inativo,
`assert` usado como validação e bind de desenvolvimento em todas as interfaces.
Esses pontos foram corrigidos antes da execução final.

## Remediação das dependências do frontend

A revisão final encontrou que a etapa npm existia no CI, mas estava marcada com
`continue-on-error`. Por isso, a pipeline permanecia verde mesmo quando
`npm audit` retornava erro.

Resultado inicial observado:

| Severidade | Quantidade |
|---|---:|
| Baixa | 1 |
| Moderada | 17 |
| Alta | 19 |
| Crítica | 2 |
| **Total** | **39** |

Um `npm audit fix` conservador reduziu o total para 17, mas não eliminou quatro
vulnerabilidades altas. A correção final atualizou em conjunto Firebase, Vite,
plugin React, TypeScript, TypeScript ESLint e React Router, removeu a dependência
`uuid` não utilizada e fixou a versão transitiva corrigida de
`@grpc/grpc-js`.

Validação executada após a atualização:

```text
npm ci                         concluído
npm run lint                   concluído sem erros
npm run build                  concluído
npm audit --audit-level=high   found 0 vulnerabilities
```

A auditoria agora é bloqueante: novas vulnerabilidades altas ou críticas fazem o
job do frontend falhar.

## Infraestrutura

A validação de runtime é executada no GitHub Actions:

- `docker compose config` valida a configuração;
- as imagens de backend e frontend são construídas;
- Nginx, frontend e duas réplicas do backend são iniciados;
- oito requisições precisam alcançar `backend-1` e `backend-2`;
- o smoke test confirma HTTP 401 sem token e headers de segurança ativos;
- os containers são encerrados e os volumes temporários removidos.

Saída sanitizada: [evidência de balanceamento](evidence/LOAD-BALANCING.md).

Os comandos de reprodução estão em [REPRODUCTION.md](REPRODUCTION.md). Nenhum
resultado de ferramenta foi inventado ou marcado como aprovado sem execução.
