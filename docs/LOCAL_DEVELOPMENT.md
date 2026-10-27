# Desenvolvimento local sem Docker

O Docker Compose é o caminho recomendado. Estas instruções servem para alterar e testar backend e frontend separadamente.

## Backend

Requisitos: Python 3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
python backend/endpoints.py
```

Por padrão, a API escuta apenas `127.0.0.1:5000`. Endpoints disponíveis sem integrações externas:

- `http://127.0.0.1:5000/health`
- `http://127.0.0.1:5000/metrics`

Validação:

```bash
pytest -q backend/tests
python -m compileall -q backend
bandit -q -r backend -x backend/tests
pip-audit -r backend/requirements.txt
```

## Frontend

Requisitos: Node.js 20 ou superior.

```bash
cd frontend
cp .env.example .env
npm ci
npm run dev
```

Configure `VITE_API_BASE_URL=http://127.0.0.1:5000`. Os placeholders Firebase permitem o build, mas login e perfil exigem um projeto próprio e autorizado.

Validação:

```bash
npm run lint
npm run build
npm audit --audit-level=high
```

## Integrações autorizadas

Variáveis do backend:

```bash
export OPENAI_API_KEY="sua-chave"
export FIREBASE_CREDENTIALS_PATH="/caminho/credentials.json"
export FIREBASE_DATABASE_URL="https://seu-projeto.firebaseio.com"
```

Nunca use valores encontrados no repositório de referência. `.env`, `credentials.json` e arquivos de chave são ignorados pelo Git.

## Configurações de segurança

- `CORS_ALLOWED_ORIGINS`: lista separada por vírgula;
- `CREATE_USER_RATE_LIMIT`: tentativas por janela;
- `CREATE_USER_RATE_WINDOW`: janela em segundos;
- `ENABLE_HSTS`: habilite somente atrás de HTTPS;
- `TRUST_PROXY_HEADERS`: habilite somente atrás de proxy controlado;
- `INSTANCE_ID`: identificação usada em logs e métricas.
