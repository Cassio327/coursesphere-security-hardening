# Relatório técnico de segurança e confiabilidade

**Aplicação:** CourseSphere  
**Referência analisada:** `LambdaAK/CourseSphere@71616a08b8756f048d5bf237be433c3b996a43d1`  
**Baseline reproduzível deste repositório:** `f0765ae1f97a48d19f25b37debc033fe4bd5160f`  
**Data da avaliação:** 27/10/2026  
**Ambiente:** cópia local e isolada

## 1. Resumo executivo

A avaliação confirmou cinco vulnerabilidades em quatro categorias da OWASP Top 10. O achado de maior prioridade é a presença de credenciais no código-fonte de referência. Quatro falhas da API foram corrigidas neste repositório: transporte de token na URL, CORS permissivo, exposição de detalhes internos e ausência de autenticação no endpoint de consultas.

| ID | Achado | Categoria | Severidade | Situação |
|---|---|---|---:|---|
| VULN-01 | Credencial de terceiro versionada | Dados sensíveis | Alta | Removida da cópia; rotação externa necessária |
| VULN-02 | Token de identidade transmitido na URL | Autenticação/dados sensíveis | Média | Corrigida |
| VULN-03 | Política CORS permissiva | Configuração incorreta | Média | Corrigida |
| VULN-04 | Exposição de exceções internas | Configuração incorreta | Média | Corrigida |
| VULN-05 | Consulta aceita sem autenticação | Controle de acesso | Média | Corrigida |

As correções foram acompanhadas por testes de regressão. O hardening adicional inclui rate limiting, validação de entrada, limite de payload, headers HTTP de segurança, execução dos containers sem root e verificação automatizada no CI.

## 2. Escopo e regras de segurança

### Incluído

- API Flask e seus controles de autenticação;
- comunicação do frontend React com a API;
- tratamento de erros e validação de entrada;
- configuração CORS e headers HTTP;
- arquivos de configuração e dependências;
- containerização, balanceamento e observabilidade.

### Excluído

- testes contra Firebase, OpenAI, Reddit ou qualquer serviço externo;
- utilização ou validação de credenciais encontradas no material original;
- banco de cursos, que não foi distribuído com a aplicação;
- exploração destrutiva, negação de serviço e testes em produção.

O blueprint de cursos continha consultas construídas por interpolação, mas não estava registrado e o banco não estava presente. Portanto, esse código não foi contabilizado como vulnerabilidade explorável. Mesmo assim, as consultas foram parametrizadas como defesa preventiva.

## 3. Metodologia

1. Preservação de uma baseline sanitizada e registro do commit de origem.
2. Revisão manual orientada pelas categorias OWASP Top 10.
3. Reprodução dinâmica com o test client do Flask, sem tráfego externo.
4. Classificação por impacto, pré-condições e facilidade de exploração.
5. Correção da causa raiz e criação de testes de regressão.
6. SAST com Bandit, SCA com `pip-audit` e auditoria npm no pipeline.
7. Validação de build, testes, configuração de infraestrutura e documentação.

As pontuações CVSS são estimativas para priorização e devem ser recalculadas com o contexto definitivo de implantação.

## 4. Achados

### VULN-01 — Credencial de terceiro versionada

- **Severidade:** Alta — CVSS estimado 8.1
- **CWE:** CWE-798, uso de credencial embutida
- **OWASP:** A02 — Cryptographic Failures
- **Local:** material de dados do repositório de referência

O repositório original continha um arquivo JSON com identificadores de cliente de uma integração Reddit. Apenas o caminho e os nomes das chaves foram registrados; nenhum valor foi copiado para este projeto.

**Impacto de negócio:** uso indevido da integração, consumo de cotas, coleta não autorizada e possível associação do abuso ao proprietário legítimo.

**Causa raiz:** segredo tratado como arquivo comum e incluído no controle de versão.

**Tratamento:** o arquivo foi excluído antes do primeiro commit desta cópia, padrões de segredo foram adicionados ao `.gitignore` e o CI executa Gitleaks. A rotação/revogação precisa ser feita pelo proprietário da credencial original, pois este projeto não tem autorização sobre a conta externa.

**Evidência:** [VULN-01](evidence/VULN-01-secret-in-source.md)

### VULN-02 — Token de identidade transmitido na URL

- **Severidade:** Média — CVSS estimado 6.5
- **CWE:** CWE-598, informação sensível em query string
- **OWASP:** A07 — Identification and Authentication Failures
- **Local:** `GET /users/info` e `frontend/src/api.ts`

O frontend enviava `id_token` na query string. URLs podem aparecer em histórico, logs de proxy, ferramentas de monitoramento e referências HTTP.

**Impacto de negócio:** um token capturado dentro de sua validade pode permitir acesso ao perfil do usuário.

**Causa raiz:** ausência de um contrato único de autenticação entre frontend e backend.

**Correção:** todas as rotas protegidas utilizam exclusivamente `Authorization: Bearer <token>`. O parâmetro de URL não é mais aceito e existe teste específico para impedir regressão.

**Evidência:** [VULN-02](evidence/VULN-02-token-in-url.md)

### VULN-03 — Política CORS permissiva

- **Severidade:** Média — CVSS estimado 5.3
- **CWE:** CWE-942, política de origem cruzada permissiva
- **OWASP:** A05 — Security Misconfiguration
- **Local:** inicialização Flask

O uso de `CORS(app)` aceitava origens arbitrárias. Isso ampliava desnecessariamente quais aplicações web poderiam ler respostas da API no navegador.

**Impacto de negócio:** aumenta a superfície para abuso de endpoints públicos e agrava o impacto caso um token seja exposto por outro vetor.

**Causa raiz:** middleware habilitado globalmente sem allowlist.

**Correção:** allowlist definida por `CORS_ALLOWED_ORIGINS`, métodos e headers explícitos e credenciais de navegador desabilitadas. O teste compara uma origem autorizada e uma origem não confiável.

**Evidência:** [VULN-03](evidence/VULN-03-permissive-cors.md)

### VULN-04 — Exposição de exceções internas

- **Severidade:** Média — CVSS estimado 5.3
- **CWE:** CWE-209, geração de mensagem com informação sensível
- **OWASP:** A05 — Security Misconfiguration
- **Local:** tratamento de exceções das rotas

As rotas retornavam `str(e)` ao cliente. Na baseline, a resposta revelava nomes de variáveis de ambiente e detalhes da configuração Firebase ausente.

**Impacto de negócio:** facilita reconhecimento da arquitetura e pode revelar caminhos, fornecedores, regras internas ou dados presentes em exceções futuras.

**Causa raiz:** a mesma mensagem de exceção era usada para diagnóstico interno e resposta pública.

**Correção:** respostas usam códigos e mensagens estáveis; detalhes completos permanecem somente nos logs estruturados. Um teste injeta uma exceção com caminho sensível e comprova que esse texto não aparece na resposta.

**Evidência:** [VULN-04](evidence/VULN-04-error-disclosure.md)

### VULN-05 — Endpoint de consulta sem autenticação obrigatória

- **Severidade:** Média — CVSS estimado 6.5
- **CWE:** CWE-306, ausência de autenticação em função crítica
- **OWASP:** A01 — Broken Access Control
- **Local:** `POST /users/query`

A API aceitava consultas sem token válido e devolvia HTTP 200. A implementação atual do gerenciador é simulada, mas a função foi projetada para consumir um provedor de IA e informações de perfil.

**Impacto de negócio:** em uma implementação completa, permitiria consumo anônimo de recursos pagos, automação abusiva e execução de consultas sem vínculo auditável com um usuário.

**Causa raiz:** autenticação era opcional; a aplicação tentava buscar perfil e continuava quando a verificação falhava.

**Correção:** a rota exige um Bearer token válido antes de processar a entrada. A identidade verificada é reutilizada para carregar somente o perfil correspondente.

**Evidência:** [VULN-05](evidence/VULN-05-missing-authentication.md)

## 5. Hardening adicional

| Controle | Implementação | Risco reduzido |
|---|---|---|
| Rate limiting | Cinco criações de usuário por minuto e origem | automação e abuso básico |
| Headers HTTP | CSP, `nosniff`, `DENY`, Referrer e Permissions Policy | clickjacking e interpretação indevida |
| Validação de entrada | tipos, tamanhos, formato de e-mail e payload de 16 KiB | entradas malformadas e consumo excessivo |
| SQL parametrizado | placeholders SQLite no blueprint de cursos | injeção caso o módulo seja ativado |
| Containers sem root | usuário dedicado, `cap_drop` e `no-new-privileges` | impacto de comprometimento do processo |
| Detecção de segredos | Gitleaks no CI e arquivos sensíveis ignorados | nova exposição acidental |

O rate limiter em memória atende ao ambiente isolado do desafio. Em produção com múltiplas réplicas, deve ser substituído por estado compartilhado em Redis ou aplicado no API Gateway.

## 6. Confiabilidade

Foram implementados logs JSON, correlação por `X-Request-ID`, `/health`, `/metrics`, duas réplicas da API, Nginx com balanceamento, Prometheus e dashboard Grafana provisionado. Definições formais dos indicadores e riscos estão em [OBSERVABILITY.md](OBSERVABILITY.md).

## 7. Priorização recomendada

1. Revogar e substituir qualquer credencial que ainda esteja válida no projeto de origem.
2. Manter autenticação, mensagens de erro e política CORS como bloqueios obrigatórios de CI.
3. Configurar credenciais Firebase próprias por secret manager, sem arquivos versionados.
4. Trocar rate limiting local por armazenamento compartilhado antes de escalar horizontalmente.
5. Definir alertas baseados no consumo do error budget e testar falha de uma instância.
6. Ativar TLS no ponto de entrada e HSTS somente no ambiente HTTPS.

## 8. Limitações e risco residual

- Firebase e OpenAI não foram exercitados por falta de credenciais próprias e por regra de isolamento.
- A autenticação depende da disponibilidade e das garantias do Firebase.
- O conteúdo funcional de cursos não pode ser validado sem o banco original.
- O Docker Compose foi validado estruturalmente neste ambiente, mas a execução completa deve ser confirmada em host com Docker.
- O rate limiter local não compartilha contadores entre réplicas.
- A aplicação ainda precisa de TLS e gestão centralizada de segredos para um cenário produtivo.

## 9. Validação

Os comandos, resultados observados e limitações estão em [TOOL_RESULTS.md](TOOL_RESULTS.md). A reprodução segura dos achados e a execução da versão corrigida estão descritas no [README](../README.md).
