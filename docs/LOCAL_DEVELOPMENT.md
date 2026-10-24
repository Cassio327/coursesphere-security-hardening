# Desenvolvimento local

Este documento descreve o ambiente utilizado para reproduzir e corrigir os bloqueios iniciais do CourseSphere.

## Versões testadas

- Python 3.12.14
- Node.js 24.22.1
- npm 11.9.0

## Frontend

Prepare o arquivo local de configuração:

```bash
cd frontend
cp .env.example .env
npm ci
```

O arquivo `.env` não deve ser enviado ao GitHub. Os valores de exemplo permitem gerar o build, mas as funcionalidades do Firebase exigem uma configuração própria e autorizada.

Comandos de validação:

```bash
npm run lint
npm run build
```

Resultado obtido:

- lint concluído sem erros;
- build de produção concluído;
- aviso de bundle acima de 500 kB mantido para otimização futura.

Para abrir o servidor de desenvolvimento:

```bash
npm run dev
```

## Backend

Crie um ambiente virtual e instale as versões registradas:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python endpoints.py
```

A API inicia sem arquivos privados. Firebase e OpenAI são carregados somente quando uma operação dependente dessas integrações é executada.

Para utilizar integrações externas em um ambiente autorizado, configure:

```bash
export OPENAI_API_KEY="sua-chave"
export FIREBASE_CREDENTIALS_PATH="/caminho/credentials.json"
export FIREBASE_DATABASE_URL="https://seu-projeto.firebaseio.com"
```

Nunca utilize valores do repositório de referência.

## Validação sem serviços externos

A importação e o mapa de rotas podem ser verificados com:

```bash
python -c "import sys; sys.path.insert(0, 'backend'); from endpoints import app; print(app.url_map)"
```

O teste confirma que o Flask carrega as rotas sem tentar conectar ao Firebase ou à OpenAI durante a importação.

## Limitações atuais

- rotas que dependem do Firebase não funcionam sem configuração própria;
- a resposta do gerenciador de consultas ainda é uma implementação simulada;
- o blueprint de cursos ainda não está registrado;
- o servidor Flask permanece com configurações originais que serão avaliadas na etapa de segurança;
- Docker e balanceamento serão tratados em uma etapa posterior.
