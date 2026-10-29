# Roteiro de reprodução segura

Este roteiro demonstra os cinco achados sem utilizar credenciais reais e sem enviar
requisições a Firebase, OpenAI, Reddit ou qualquer outro serviço externo.

## 1. Preparar os ambientes

Na raiz deste repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
pytest -q backend/tests
```

Crie um worktree somente para observar o comportamento anterior às correções:

```bash
git worktree add ../coursesphere-baseline f0765ae1f97a48d19f25b37debc033fe4bd5160f
python3 -m venv ../coursesphere-baseline/.venv
../coursesphere-baseline/.venv/bin/pip install   -r ../coursesphere-baseline/backend/requirements.txt
```

Os comandos de demonstração dinâmica abaixo usam o test client do Flask e permanecem
na máquina local.

## 2. VULN-01 — credencial versionada

Confirme apenas a existência e o caminho do arquivo no commit de referência, sem
fazer checkout nem exibir seu conteúdo:

```bash
git clone --no-checkout https://github.com/LambdaAK/CourseSphere.git   ../CourseSphere-reference
git -C ../CourseSphere-reference ls-tree -r   71616a08b8756f048d5bf237be433c3b996a43d1 --name-only   | grep 'reddit_key.json'
```

Resultado esperado: o caminho
`backend/cornell-course-sphere-data/reddit-data/reddit_key.json`.

Confirme que a cópia corrigida não rastreia arquivos equivalentes:

```bash
git ls-files | grep -E 'reddit_key|credentials\.json|\.env$'
```

Resultado esperado: nenhuma ocorrência. A remoção do arquivo não substitui a
revogação da credencial pelo proprietário original.

## 3. VULN-02 — token transmitido na URL

Localize o contrato vulnerável na baseline:

```bash
git -C ../coursesphere-baseline grep -n 'id_token' --   backend frontend/src
```

O resultado mostra o frontend anexando o token à URL e o backend lendo
`request.args`. Na versão corrigida, execute a regressão que comprova que query
string não é aceita como autenticação:

```bash
pytest -q backend/tests -k token_in_query_string
```

Resultado esperado: teste aprovado; sem o header `Authorization`, a resposta é
HTTP 401.

## 4. VULN-03 — CORS permissivo

Execute na baseline:

```bash
cd ../coursesphere-baseline/backend
../.venv/bin/python -c "from endpoints import app; c=app.test_client(); r=c.get('/users/info', headers={'Origin':'https://attacker.example'}); print(r.headers.get('Access-Control-Allow-Origin'))"
cd ../../coursesphere-security-hardening
```

Resultado esperado na baseline: `https://attacker.example`, apesar de a origem não
ter sido autorizada. Valide a allowlist da versão corrigida:

```bash
pytest -q backend/tests -k cors_allows_only_configured_origin
```

## 5. VULN-04 — detalhes internos na resposta

Execute na baseline com dados fictícios:

```bash
cd ../coursesphere-baseline/backend
../.venv/bin/python -c "from endpoints import app; c=app.test_client(); r=c.post('/users/create', json={'email':'candidate@example.com','password':'long-password'}); print(r.status_code, r.get_json())"
cd ../../coursesphere-security-hardening
```

A resposta anterior inclui detalhes da exceção de configuração. Não copie esses
detalhes para relatórios públicos. Valide a separação entre erro público e log
interno na versão corrigida:

```bash
pytest -q backend/tests -k internal_exception_is_not_exposed
```

## 6. VULN-05 — consulta sem autenticação

Execute na baseline:

```bash
cd ../coursesphere-baseline/backend
../.venv/bin/python -c "from endpoints import app; c=app.test_client(); r=c.post('/users/query', json={'query':'local test'}); print(r.status_code, r.get_json())"
cd ../../coursesphere-security-hardening
```

Resultado histórico esperado: HTTP 200 sem Bearer token. Valide a correção:

```bash
pytest -q backend/tests -k 'protected_query_rejects_missing_token or valid_bearer_token_allows_query'
```

Resultado esperado: acesso anônimo rejeitado com HTTP 401 e acesso autenticado
simulado pelo teste permitido.

## 7. Validar a solução completa

```bash
pytest -q backend/tests
bandit -q -r backend -x backend/tests
pip-audit -r backend/requirements.txt
cd frontend
npm ci
npm run lint
npm run build
npm audit --audit-level=high
```

Com Docker disponível, volte à raiz e valide infraestrutura e balanceamento:

```bash
cd ..
docker compose up --build -d
./scripts/demo-load-balancing.sh
./scripts/security-smoke-test.sh
docker compose down --volumes
```

## 8. Limpeza opcional

```bash
git worktree remove ../coursesphere-baseline
rm -rf ../CourseSphere-reference
```

A última linha remove apenas o clone descartável criado neste roteiro.
