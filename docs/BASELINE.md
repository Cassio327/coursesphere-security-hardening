# Baseline do projeto

## Origem

- Repositório de referência: https://github.com/LambdaAK/CourseSphere
- Branch analisada: `main`
- Commit de referência: `71616a08b8756f048d5bf237be433c3b996a43d1`
- Data da importação: 23/10/2026
- Ambiente de análise: cópia local e isolada

## Objetivo desta etapa

Preservar uma versão reconhecível do CourseSphere para análise, sem copiar credenciais, histórico Git ou arquivos que possam provocar acesso acidental a serviços externos.

## Conteúdo preservado

- código do backend Flask;
- código do frontend React e TypeScript;
- arquivos de dependências;
- configuração original de build;
- rotas de usuários, chats e cursos;
- integração com Firebase representada por variáveis de ambiente.

## Conteúdo não importado

- histórico Git do repositório original;
- arquivos de IDE e sistema operacional;
- caches e artefatos de build;
- notebooks experimentais;
- conjuntos de dados coletados de fontes externas;
- arquivo que continha credenciais do Reddit;
- valores de configuração associados ao projeto Firebase original.

Os dados e notebooks não são necessários para reproduzir o escopo de autenticação, API e interface selecionado para o desafio.

## Sanitização anterior ao primeiro commit

A configuração Firebase do frontend foi convertida para variáveis `VITE_FIREBASE_*`. Um arquivo `.env.example` contém apenas valores fictícios. Essa alteração foi realizada antes da publicação para evitar que a cópia do projeto interagisse acidentalmente com a infraestrutura dos autores.

A exposição de credenciais observada no repositório de referência será analisada no relatório sem reproduzir os valores encontrados.

## Limitações iniciais conhecidas

A inspeção preliminar identificou os seguintes bloqueios funcionais:

- erros TypeScript impedem o build do frontend;
- o backend depende de arquivos locais de configuração não fornecidos;
- `numpy` é utilizado diretamente, mas não aparece em `backend/requirements.txt`;
- código da OpenAI é executado durante a importação de `backend/main.py`;
- o blueprint de cursos não está registrado;
- o banco SQLite referenciado não está incluído;
- não existem testes automatizados, métricas ou Dockerfile do backend.

Esses itens são limitações funcionais. Eles não serão classificados como vulnerabilidades sem demonstração de impacto de segurança.

## Reprodução do estado inicial

### Frontend

Comandos executados:

```bash
cd frontend
npm ci
npm run build
```

A instalação concluiu com 375 pacotes. O build terminou com código 2 durante a verificação TypeScript. Os erros foram agrupados em:

- imports e variáveis declaradas, mas não utilizadas;
- ausência da declaração de tipos do jQuery;
- propriedade `sectionNumber` ausente ao criar um cartão de curso;
- propriedades incompatíveis em um componente do dashboard.

Nenhum desses erros foi corrigido nesta etapa. O objetivo foi registrar o comportamento inicial.

### Backend

Comandos executados:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd backend
../.venv/bin/python endpoints.py
../.venv/bin/python main.py
```

A instalação das dependências foi concluída. A API não iniciou:

1. `endpoints.py` encerrou com `FileNotFoundError` ao importar `firebase.py`, que espera `credentials.json` no diretório atual;
2. `main.py` encerrou com `FileNotFoundError`, pois tenta abrir `config.json` durante a importação.

O arquivo `requirements.txt` não fixa versões. Portanto, uma instalação futura pode resolver versões diferentes das utilizadas nesta reprodução.

## Regra de testes

Nenhuma credencial encontrada no material original deve ser utilizada. Testes dinâmicos serão executados apenas em serviços locais controlados por este projeto.
