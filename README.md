# 💰 Controle de Finanças Pessoais

Aplicação web para registrar receitas e despesas, organizar por categorias e acompanhar o saldo mensal.
Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II).

- **Back-end:** Python 3 + Flask (padrão **MVC**, com Blueprints) + SQLAlchemy
- **Banco de dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Front-end:** HTML + CSS (templates Jinja2)
- **Testes:** pytest (30 testes automatizados)

## Como executar
```bash
cd backend
python -m venv .venv
source .venv/bin/activate      
pip install -r requirements.txt
python run.py           
```
O banco é criado automaticamente na primeira execução, com categorias padrão.

## Testes
```bash
cd backend
python -m pytest -v
```

## Estrutura do projeto
```
controle-financas/
├── backend/                  # BACK-END (Python/Flask, padrão MVC)
│   ├── app/
│   │   ├── models/           #   Model: entidades, validação e regras de negócio
│   │   └── controllers/      #   Controller: rotas e fluxo das telas
│   ├── tests/                #   testes automatizados (pytest)
│   ├── config.py · run.py · requirements.txt · Procfile
├── frontend/                 # FRONT-END (View)
│   ├── templates/            #   páginas HTML (Jinja2)
│   └── static/               #   CSS
├── database/                 # BANCO DE DADOS
│   ├── schema.sql            #   criação das tabelas (projeto físico)
│   ├── dados_iniciais.sql    #   categorias padrão
│   └── financas.db           #   arquivo SQLite (criado ao rodar; não vai ao Git)
└── docs/                     # DOCUMENTAÇÃO (requisitos, UML, banco, IHC, testes)
```
O fluxo MVC: o **controller** (backend) recebe a requisição, usa o **model** (backend) para validar e gravar
no **banco** (database) e devolve a **view** (frontend) preenchida.

## Documentação
1. [Escopo e requisitos](docs/01-escopo-e-requisitos.md)
2. [Modelagem UML](docs/02-modelagem-uml.md)
3. [Banco de dados e dicionário de dados](docs/03-banco-de-dados.md)
4. [IHC (interface)](docs/04-ihc.md)
5. [Plano de testes](docs/05-plano-de-testes.md)
6. [Formulário de teste para colegas](docs/formulario-teste-colegas.md)
7. [Modelo de laudo de qualidade](docs/06-laudo-de-qualidade-modelo.md)
8. [Roteiro dos vídeos](docs/07-roteiro-dos-videos.md)

## Publicação Render Teste 1
1. Suba o repositório no GitHub.
2. No Render, crie um **Web Service** apontando para o repositório e um banco **PostgreSQL**.
3. Root Directory: `backend` · Build: `pip install -r requirements.txt` · Start: `gunicorn run:app`
4. Variáveis de ambiente: `DATABASE_URL` (do banco) e `SECRET_KEY` (um texto aleatório).