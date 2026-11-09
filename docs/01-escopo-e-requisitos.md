# 1. Escopo e Requisitos

## 1.1 Problema
Muitas pessoas não sabem para onde vai o próprio dinheiro porque anotam gastos em papel, em
mensagens ou de cabeça. Sem visão do mês, é difícil saber se sobrou ou faltou dinheiro.

## 1.2 Solução
Aplicação web **Controle de Finanças Pessoais**: o usuário registra receitas e despesas, organiza por
categorias e vê um resumo mensal com receitas, despesas e saldo.

## 1.3 Escopo
**Dentro do escopo (versão atual)**
- Cadastro, edição, exclusão e listagem de categorias (receita ou despesa).
- Cadastro, edição, exclusão e listagem de lançamentos.
- Filtro por tipo/categoria e busca por descrição.
- Resumo mensal (receitas, despesas, saldo, total por categoria) com navegação entre meses.

**Fora do escopo (melhorias futuras)**
- Login e múltiplos usuários, metas e orçamento, exportação para planilha, gráficos, app mobile.

## 1.4 Requisitos funcionais
| ID | Requisito |
|---|---|
| RF01 | O sistema deve permitir cadastrar, editar, listar e excluir categorias. |
| RF02 | O sistema deve permitir cadastrar, editar, listar e excluir lançamentos (descrição, valor, data, categoria, observação). |
| RF03 | O sistema deve exibir o resumo mensal: total de receitas, total de despesas e saldo. |
| RF04 | O sistema deve exibir o total por categoria no mês. |
| RF05 | O sistema deve permitir navegar para o mês anterior e o próximo. |
| RF06 | O sistema deve permitir filtrar lançamentos por tipo e categoria e buscar por descrição. |
| RF07 | O sistema deve criar categorias padrão na primeira execução. |

## 1.5 Regras de negócio
| ID | Regra |
|---|---|
| RN01 | O valor do lançamento deve ser maior que zero (aceita vírgula como separador decimal). |
| RN02 | A descrição é obrigatória (até 100 caracteres). |
| RN03 | A data deve ser válida. |
| RN04 | O tipo do lançamento (receita/despesa) vem da categoria escolhida. |
| RN05 | Nomes de categoria são únicos, sem diferenciar maiúsculas/minúsculas. |
| RN06 | Não é possível excluir categoria que possui lançamentos. |
| RN07 | Não é possível mudar o tipo de uma categoria que já possui lançamentos. |
| RN08 | Saldo = receitas − despesas do mês. |

## 1.6 Requisitos não funcionais
| ID | Requisito | Como é atendido |
|---|---|---|
| RNF01 | Usabilidade: interface simples, clara e consistente | Princípios de Norman/IHC (ver `04-ihc.md`) |
| RNF02 | Confiabilidade: erros tratados com mensagem amigável | Validação no model + mensagens + página 404 |
| RNF03 | Testabilidade | 30 testes automatizados com pytest |
| RNF04 | Manutenibilidade | Arquitetura MVC com Blueprints e pastas separadas (backend, frontend, database) |
| RNF05 | Portabilidade | SQLite (dev) e PostgreSQL (produção) via SQLAlchemy |
| RNF06 | Responsividade | CSS adaptável a celular |
| RNF07 | Segurança básica | Consultas parametrizadas (ORM), escape automático no Jinja2, exclusão só via POST |
