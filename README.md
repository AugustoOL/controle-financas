# 💰 Controle de Finanças Pessoais

Um sistema web simples para você anotar o que ganha e o que gasta, organizar tudo por categorias e
ver, mês a mês, quanto sobrou (ou faltou). Foi feito como projeto do PIT II (Projeto Integrador
Transdisciplinar em Engenharia de Software II).

## 🌐 Teste online

🔗 **https://controle-financas-z5sc.onrender.com/**

O sistema está no ar na hospedagem **gratuita** do Render (servidor + banco PostgreSQL). Isso traz
alguns detalhes que vale saber antes de abrir:

- **O primeiro acesso demora.** Se ninguém usa o site por uns 15 minutos, o servidor "dorme". Na
  primeira visita depois disso, o Render mostra uma tela de carregamento e o site leva cerca de
  **1 minuto** para abrir. É só esperar: a página carrega sozinha e depois funciona normalmente.
- **O banco de dados tem prazo.** O PostgreSQL gratuito foi criado novamente e vale até
  **08/12/2026**. Depois dessa data o Render apaga o banco e o site deixa de funcionar na nuvem.
  O projeto continua funcionando normalmente na sua máquina (veja "Como rodar no seu computador").
- **Use dados de teste.** Crie uma conta com um e-mail qualquer e uma senha de teste. Não use a senha
  de nenhuma conta sua de verdade.

## ✨ O que dá para fazer

- Criar sua conta e entrar. Cada pessoa vê só os próprios dados.
- Registrar **receitas e despesas** (descrição, valor, data, categoria e observação).
- Organizar em **categorias**. Cada conta nova já vem com algumas (Salário, Alimentação, Moradia...).
- Ver o **resumo do mês**: receitas, despesas, saldo e o total por categoria, escolhendo o mês e o ano.
- Achar lançamentos com **busca e filtros** (tipo, categoria, período, valor) e ordenar como quiser.
- **Repetir um lançamento todo mês** (por exemplo o aluguel) e **excluir vários de uma vez**.
- **Exportar para CSV** e abrir no Excel.
- Usar tranquilo pelo **celular**: o layout se adapta à tela.

## 🛠️ Tecnologias

- **Back-end:** Python 3 + Flask, no padrão **MVC** (com Blueprints) e SQLAlchemy
- **Banco de dados:** SQLite no desenvolvimento e PostgreSQL na hospedagem
- **Front-end:** HTML + CSS + um pouco de JavaScript (templates Jinja2)
- **Testes:** pytest (166 testes automatizados)

## 💻 Como rodar no seu computador

Você precisa do Python 3 instalado. Dentro da pasta do projeto:

```bash
cd backend
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Mac ou Linux
source .venv/bin/activate
```

Depois instale as dependências e inicie:

```bash
pip install -r requirements.txt
python run.py
```

Abra http://127.0.0.1:5000 no navegador e clique em **Criar conta**. O banco (`database/financas.db`)
é criado sozinho na primeira execução e fica só na sua máquina.

> **Atualizando de uma versão antiga?** O sistema cria as tabelas que faltam, mas não altera as que já
> existem. Se você tem um banco de antes do login, apague o arquivo `database/financas.db` e rode de novo.

## ✅ Testes

```bash
cd backend
python -m pytest -q
```

Os testes usam um banco temporário em memória, então não mexem nos seus dados.

## 🔒 Segurança em poucas palavras

- A senha nunca é guardada como texto: só o *hash*. Mínimo de 6 caracteres.
- Cada pessoa só enxerga e altera os próprios dados. Tentar abrir algo de outra conta dá "página não encontrada".
- As telas internas exigem login, e sair (logout) é sempre por POST.
- O cookie de sessão é `HttpOnly` e `SameSite=Lax` (e `Secure` quando roda no Render).
- Em produção, defina um `SECRET_KEY` próprio.

## 📁 Estrutura do projeto

```
controle-financas/
├── backend/                  # Back-end (Python/Flask, padrão MVC)
│   ├── app/
│   │   ├── models/           #   Model: entidades, validação e regras de negócio
│   │   └── controllers/      #   Controller: rotas e fluxo das telas
│   ├── tests/                #   testes automatizados (pytest)
│   └── config.py · run.py · requirements.txt · Procfile
├── frontend/                 # Front-end (View)
│   ├── templates/            #   páginas HTML (Jinja2)
│   └── static/               #   CSS, JavaScript e imagens
├── database/                 # Banco de dados
│   ├── schema.sql            #   criação das tabelas (projeto físico)
│   ├── dados_iniciais.sql    #   categorias padrão (criadas para cada conta nova)
│   └── financas.db           #   SQLite local (criado ao rodar; não vai para o Git)
└── docs/                     # Documentação (requisitos, UML, banco, IHC, testes)
```

Como as peças conversam: o **controller** recebe o pedido, usa o **model** para validar e gravar no
**banco** e devolve a **view** (a página) já preenchida.

## 📚 Documentação

1. [Escopo e requisitos](docs/01-escopo-e-requisitos.md)
2. [Modelagem UML](docs/02-modelagem-uml.md)
3. [Banco de dados e dicionário de dados](docs/03-banco-de-dados.md)
4. [IHC (interface)](docs/04-ihc.md)
5. [Plano de testes](docs/05-plano-de-testes.md)

## 🚀 Como foi publicado no Render

Em resumo: o código está no GitHub e a cada `git push` na branch `main` o Render publica de novo sozinho.

1. No Render, crie um **Web Service** apontando para o repositório e um banco **PostgreSQL**.
2. Configure o serviço:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
3. Defina as variáveis de ambiente:
   - `DATABASE_URL`: a *Internal Database URL* do banco
   - `SECRET_KEY`: um texto aleatório e secreto

Se o banco for recriado (por exemplo, quando o gratuito expira), basta criar um novo PostgreSQL e
atualizar a `DATABASE_URL` do serviço. As tabelas são criadas sozinhas no primeiro acesso.

## 🔭 Ideias para o futuro

- Recuperação de senha e confirmação de e-mail (precisam de envio de e-mail).
- Editar vários lançamentos de uma vez e editar uma recorrência inteira.
- Metas, orçamento e gráficos.
