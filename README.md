# 💰 Controle de Finanças Pessoais

Aplicação web para registrar receitas e despesas, organizar por categorias e acompanhar o saldo mensal.
Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II).

- **Back-end:** Python 3 + Flask (padrão **MVC**, com Blueprints) + SQLAlchemy
- **Banco de dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Front-end:** HTML + CSS (templates Jinja2)
- **Testes:** pytest (59 testes automatizados)

## Como executar
```bash
cd backend
python -m venv .venv
source .venv/bin/activate      
pip install -r requirements.txt
python run.py           
```
O banco é criado automaticamente na primeira execução. Cada usuário novo (tela **Criar conta**) recebe as categorias padrão.

> ⚠️ **Banco antigo (de antes do login):** `db.create_all()` não altera tabelas já existentes, então o banco anterior não funciona com a versão com login.
> - **Local:** apague o arquivo `database/financas.db` e rode de novo.
> - **Render:** apague o banco `financas-db`, crie um novo PostgreSQL (Free, mesma região) e atualize a variável `DATABASE_URL` do Web Service com a nova *Internal Database URL* (isso também reinicia o prazo de validade do banco gratuito).

## Login e segurança
- Cadastro e login por e-mail e senha (senha guardada só como *hash*; mínimo de 6 caracteres).
- Cada usuário vê e altera apenas os próprios lançamentos e categorias; itens de outro usuário respondem 404.
- Telas de resumo, lançamentos e categorias exigem login. O logout é por POST.
- Cookie de sessão `HttpOnly` + `SameSite=Lax`, e `Secure` quando a variável `RENDER` existe. Defina um `SECRET_KEY` próprio em produção.

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
│   ├── dados_iniciais.sql    #   categorias padrão (criadas por usuário)
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