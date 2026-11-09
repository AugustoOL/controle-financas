# 3. Projeto de Banco de Dados

SGBD: **PostgreSQL** em produção e **SQLite** em desenvolvimento (ambos populares e de fácil manutenção),
acessados pelo ORM SQLAlchemy.

## 3.1 Projeto conceitual (DER)
```mermaid
erDiagram
    USUARIO ||--o{ CATEGORIA : possui
    USUARIO ||--o{ LANCAMENTO : possui
    CATEGORIA ||--o{ LANCAMENTO : classifica
    USUARIO {
        int id PK
        string nome
        string email UK
        string senha_hash
    }
    CATEGORIA {
        int id PK
        string nome "UK junto com usuario_id"
        string tipo
        int usuario_id FK
    }
    LANCAMENTO {
        int id PK
        string descricao
        decimal valor
        date data
        string observacao
        int categoria_id FK
        int usuario_id FK
    }
```
Um usuário possui zero ou muitas categorias e zero ou muitos lançamentos. Uma categoria classifica zero ou muitos lançamentos; cada lançamento pertence a exatamente uma categoria e a exatamente um usuário (a categoria escolhida deve ser do mesmo usuário, regra verificada no model).

## 3.2 Projeto lógico (normalizado)
- `usuario (id PK, nome, email UNIQUE, senha_hash)`
- `categoria (id PK, nome, tipo, usuario_id FK → usuario.id, UNIQUE (usuario_id, nome))`
- `lancamento (id PK, descricao, valor, data, observacao, categoria_id FK → categoria.id, usuario_id FK → usuario.id)`

**Normalização**
- **1FN:** todos os atributos são atômicos (sem listas ou grupos repetidos).
- **2FN:** todas as chaves primárias são simples, então não há dependência parcial.
- **3FN:** o tipo (receita/despesa) depende da categoria e fica só em `categoria`. Não é repetido em
  `lancamento`, o que evita redundância e inconsistência (o tipo do lançamento é obtido pela categoria).

## 3.3 Projeto físico
O script completo está em [`database/schema.sql`](../database/schema.sql). A carga inicial (categorias padrão de um usuário) está em [`database/dados_iniciais.sql`](../database/dados_iniciais.sql); o aplicativo a executa sozinho para cada novo usuário.

## 3.4 Dicionário de dados

### Tabela `usuario`
| Campo | Tipo | Tamanho | Nulo? | Chave | Domínio / Regra | Descrição |
|---|---|---|---|---|---|---|
| id | INTEGER | – | Não | PK | Autoincremento | Identificador do usuário |
| nome | VARCHAR | 80 | Não | – | Texto não vazio (RN09) | Nome exibido no menu |
| email | VARCHAR | 120 | Não | UNIQUE | Formato válido; guardado em minúsculas; único (RN09, RN10) | E-mail usado no login |
| senha_hash | VARCHAR | 255 | Não | – | Hash gerado por `werkzeug.security`; senha original com mínimo de 6 caracteres (RN11) | Senha protegida (nunca guardada pura) |

### Tabela `categoria`
| Campo | Tipo | Tamanho | Nulo? | Chave | Domínio / Regra | Descrição |
|---|---|---|---|---|---|---|
| id | INTEGER | – | Não | PK | Autoincremento | Identificador da categoria |
| nome | VARCHAR | 50 | Não | UNIQUE com `usuario_id` | Texto não vazio; único por usuário, sem diferenciar maiúsculas/minúsculas (RN05) | Nome da categoria |
| tipo | VARCHAR | 10 | Não | – | `receita` ou `despesa` | Natureza da categoria |
| usuario_id | INTEGER | – | Não | FK → usuario.id | Usuário existente | Dono da categoria |

### Tabela `lancamento`
| Campo | Tipo | Tamanho | Nulo? | Chave | Domínio / Regra | Descrição |
|---|---|---|---|---|---|---|
| id | INTEGER | – | Não | PK | Autoincremento | Identificador do lançamento |
| descricao | VARCHAR | 100 | Não | – | Texto não vazio | O que foi recebido ou pago |
| valor | NUMERIC | 10,2 | Não | – | Maior que zero, até 99.999.999,99 | Valor em reais |
| data | DATE | – | Não | – | Data válida | Data do recebimento/pagamento |
| observacao | VARCHAR | 255 | Sim | – | Texto livre | Detalhe opcional |
| categoria_id | INTEGER | – | Não | FK → categoria.id | Categoria existente e do mesmo usuário (RN12) | Categoria do lançamento |
| usuario_id | INTEGER | – | Não | FK → usuario.id | Usuário existente | Dono do lançamento (base do isolamento, RN12) |

### Relacionamento
| Origem | Destino | Cardinalidade | Regra de integridade |
|---|---|---|---|
| usuario.id | categoria.usuario_id | 1 : N | Cada categoria pertence a um usuário |
| usuario.id | lancamento.usuario_id | 1 : N | Cada lançamento pertence a um usuário; consultas sempre filtram por ele (RN12) |
| categoria.id | lancamento.categoria_id | 1 : N | Categoria com lançamentos não pode ser excluída (RN06) |

### Categorias padrão (criadas para cada novo usuário)
Receitas: Salário, Renda extra. Despesas: Alimentação, Moradia, Transporte, Lazer, Saúde.
