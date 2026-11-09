# 2. Modelagem UML

> Os diagramas usam Mermaid e são exibidos automaticamente no GitHub.

## 2.1 Casos de uso
```mermaid
flowchart LR
    U((Usuário))
    subgraph Sistema["Controle de Finanças"]
        UC0([Cadastrar e entrar])
        UC1([Gerenciar categorias])
        UC2([Registrar lançamento])
        UC3([Editar / excluir lançamento])
        UC4([Consultar e filtrar lançamentos])
        UC5([Ver resumo mensal])
        UC6([Navegar entre meses])
    end
    U --- UC0
    U --- UC1
    U --- UC2
    U --- UC3
    U --- UC4
    U --- UC5
    UC5 -. include .-> UC6
```

| Caso de uso | Fluxo principal | Fluxo de exceção |
|---|---|---|
| **Cadastrar e entrar** | 1. Usuário abre "Criar conta". 2. Informa nome, e-mail, senha e confirmação. 3. Sistema valida, grava a senha como hash, cria as categorias padrão do usuário e já o deixa logado. Depois, para voltar: "Entrar" com e-mail e senha; "Sair" encerra a sessão. | E-mail repetido, senha com menos de 6 caracteres, senhas diferentes ou e-mail inválido: o sistema mostra o erro e mantém nome e e-mail. Login errado: "E-mail ou senha incorretos.". Sem login, qualquer tela interna leva a "Faça login para continuar." |
| **Registrar lançamento** | 1. Usuário abre "Novo lançamento". 2. Preenche descrição, valor, data e categoria. 3. Confirma. 4. Sistema valida, grava e exibe mensagem de sucesso. | Dado inválido (ex.: valor ≤ 0): o sistema mostra o erro e mantém o que o usuário digitou. |
| **Gerenciar categorias** | Criar, editar ou excluir categoria. | Nome repetido ou exclusão de categoria em uso: o sistema bloqueia e explica o motivo. |
| **Ver resumo mensal** | Usuário abre a página inicial; o sistema calcula receitas, despesas, saldo e totais por categoria do mês atual. | Mês sem dados: mensagem "Nenhum lançamento neste mês ainda". |

## 2.2 Diagrama de classes
```mermaid
classDiagram
    class Usuario {
        +int id
        +string nome
        +string email
        +string senha_hash
        +cadastrar(nome, email, senha, confirmacao)$ Usuario
        +autenticar(email, senha)$ Usuario
        +validar(nome, email, senha, confirmacao)$
    }
    class Categoria {
        +int id
        +string nome
        +string tipo
        +int usuario_id
        +criar(usuario_id, nome, tipo)$ Categoria
        +atualizar(nome, tipo)
        +excluir()
        +validar(nome, tipo)$
    }
    class Lancamento {
        +int id
        +string descricao
        +decimal valor
        +date data
        +string observacao
        +int categoria_id
        +int usuario_id
        +tipo() string
        +criar(usuario_id, descricao, valor, data, categoria_id, observacao)$ Lancamento
        +atualizar(...)
        +excluir()
        +do_mes(usuario_id, ano, mes)$ List
        +resumo(lancamentos)$ dict
    }
    class ValidacaoError
    Usuario "1" --> "0..*" Categoria : possui
    Usuario "1" --> "0..*" Lancamento : possui
    Categoria "1" --> "0..*" Lancamento : classifica
    Usuario ..> ValidacaoError : lança
    Lancamento ..> ValidacaoError : lança
    Categoria ..> ValidacaoError : lança
```

## 2.3 Diagrama de sequência — registrar lançamento
```mermaid
sequenceDiagram
    actor U as Usuário
    participant V as View (form.html)
    participant C as Controller (lancamentos)
    participant M as Model (Lancamento)
    participant DB as Banco de dados
    U->>V: Preenche e envia o formulário
    V->>C: POST /lancamentos/novo
    C->>M: Lancamento.criar(usuario_logado, dados)
    M->>M: validar(dados)
    alt dados inválidos
        M-->>C: ValidacaoError
        C-->>V: Reexibe formulário + mensagem de erro
    else dados válidos
        M->>DB: INSERT lancamento
        DB-->>M: ok
        M-->>C: lançamento criado
        C-->>U: Redireciona para a lista + "registrado com sucesso"
    end
```

## 2.4 Diagrama de atividades — resumo mensal
```mermaid
flowchart TD
    A([Início]) --> B[Usuário logado abre a página inicial]
    B --> C{Mês/ano informado e válido?}
    C -- Não --> D[Usa o mês atual]
    C -- Sim --> E[Usa o mês informado]
    D --> F[Busca os lançamentos do mês do usuário logado]
    E --> F
    F --> G[Soma receitas e despesas]
    G --> H[Calcula saldo e total por categoria]
    H --> I{Há lançamentos?}
    I -- Sim --> J[Exibe cards, tabela por categoria e últimos lançamentos]
    I -- Não --> K[Exibe mensagem de mês vazio]
    J --> L([Fim])
    K --> L
```

## 2.5 Arquitetura MVC
```mermaid
flowchart LR
    U[Usuário] -->|Requisição HTTP| R[Router / Blueprints]
    R --> C[Controller]
    C <-->|dados| M[Model + regras]
    M <--> DB[(Banco de dados)]
    C -->|dados| V[View - templates Jinja2]
    V -->|HTML| U
```
| Camada | Pasta | Responsabilidade |
|---|---|---|
| Model | `backend/app/models/` | Entidades, validação, regras de negócio e consultas |
| View | `frontend/templates/` + `frontend/static/` | HTML (Jinja2) e CSS |
| Controller | `backend/app/controllers/` | Recebe a requisição, chama o model, escolhe a view |
