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
- Cadastro de usuário, login e logout, com dados separados por usuário.
- Máscara de valor em reais; filtros de lançamentos por data, valor e ordenação; paginação; total do que está filtrado; exportação para CSV.
- Lançamento recorrente (repetir todo mês) e exclusão de vários lançamentos de uma vez.
- Filtro de categorias por tipo e seletor de mês/ano no resumo.
- Interface adaptada ao celular (cabeçalho fixo, tabelas em formato de cartão).

**Fora do escopo (melhorias futuras)**
- **Recuperação de senha** e confirmação de e-mail (exigem envio de e-mail, que o projeto não tem).
- Metas e orçamento, gráficos, app mobile nativo.
- Edição de lançamentos recorrentes em grupo (cada repetição é um lançamento independente) e edição em lote.

## 1.4 Requisitos funcionais
| ID | Requisito |
|---|---|
| RF01 | O sistema deve permitir cadastrar, editar, listar e excluir categorias. |
| RF02 | O sistema deve permitir cadastrar, editar, listar e excluir lançamentos (descrição, valor, data, categoria, observação). |
| RF03 | O sistema deve exibir o resumo mensal: total de receitas, total de despesas e saldo. |
| RF04 | O sistema deve exibir o total por categoria no mês. |
| RF05 | O sistema deve permitir navegar para o mês anterior e o próximo. |
| RF06 | O sistema deve permitir filtrar lançamentos por tipo e categoria e buscar por descrição. |
| RF07 | O sistema deve criar as categorias padrão para cada novo usuário no momento do cadastro. |
| RF08 | O sistema deve permitir cadastrar um usuário (nome, e-mail, senha e confirmação de senha). |
| RF09 | O sistema deve permitir entrar (login) e sair (logout) da conta. |
| RF10 | O sistema deve permitir acesso ao resumo, lançamentos e categorias somente a usuários logados; quem não está logado é levado à tela de login. |
| RF11 | Cada usuário deve ver e alterar somente os seus próprios lançamentos e categorias. |
| RF12 | O campo "Valor" deve ter máscara em reais (1.234,56) ao digitar e vir formatado na edição. |
| RF13 | O formulário deve explicar o campo de data ("Data da compra ou do recebimento" + texto de ajuda). |
| RF14 | A lista de lançamentos deve poder ser filtrada por data (de/até) e valor (mínimo/máximo) e ordenada por data, valor ou descrição, crescente ou decrescente, além da busca, tipo e categoria. Filtro inválido é ignorado com mensagem amigável. |
| RF15 | A lista de categorias deve poder ser filtrada por tipo. |
| RF16 | O resumo deve permitir escolher mês e ano por seletor. Mês/ano inválidos levam ao mês atual, sem erro. |
| RF17 | O cabeçalho deve ficar fixo e as telas devem funcionar no celular sem rolagem horizontal (tabelas viram cartões). |
| RF18 | O novo lançamento pode ser repetido todo mês por até 60 meses; cada repetição vira um lançamento ("Aluguel (2/12)"). |
| RF19 | O usuário pode selecionar vários lançamentos da lista e excluí-los de uma vez, com confirmação. |
| RF20 | A lista de lançamentos é paginada (20 por página) e mostra o total de lançamentos, receitas, despesas e saldo de tudo o que está filtrado. |
| RF21 | O usuário pode exportar para CSV (abre no Excel) os lançamentos filtrados. |

## 1.5 Regras de negócio
| ID | Regra |
|---|---|
| RN01 | O valor do lançamento deve ser maior que zero (aceita vírgula como separador decimal). |
| RN02 | A descrição é obrigatória (até 100 caracteres). |
| RN03 | A data deve ser válida. |
| RN04 | O tipo do lançamento (receita/despesa) vem da categoria escolhida. |
| RN05 | Nomes de categoria são únicos **por usuário**, sem diferenciar maiúsculas/minúsculas. |
| RN06 | Não é possível excluir categoria que possui lançamentos. |
| RN07 | Não é possível mudar o tipo de uma categoria que já possui lançamentos. |
| RN08 | Saldo = receitas − despesas do mês. |
| RN09 | O nome do usuário é obrigatório (até 80 caracteres) e o e-mail deve ter formato válido. |
| RN10 | O e-mail é único no sistema, sem diferenciar maiúsculas/minúsculas (é guardado em minúsculas). |
| RN11 | A senha deve ter no mínimo 6 caracteres e a confirmação deve ser igual. A senha nunca é guardada pura: só o *hash* (werkzeug). |
| RN12 | Isolamento: toda consulta é filtrada pelo usuário logado. Abrir, editar ou excluir item de outro usuário responde 404. A categoria de um lançamento deve pertencer ao próprio usuário. |
| RN13 | A mensagem de login incorreto é genérica ("E-mail ou senha incorretos."), sem revelar se o e-mail existe. |
| RN14 | Formato do valor: com vírgula, os pontos são milhar (`1.234,56`); sem vírgula, `1.234` = 1234 (ponto com 3 casas é milhar) e `10.5`/`1234.56` têm ponto decimal (1 ou 2 casas). São recusados texto, negativos, `nan`/`inf`, notação científica (`1e3`) e mais de 2 casas decimais (`0,001`). |
| RN15 | Filtros inválidos (data, valor mínimo/máximo, intervalo invertido) são ignorados com mensagem; os filtros sempre atuam só sobre os dados do usuário logado. |
| RN16 | A data do lançamento deve estar entre 01/01/2000 e 10 anos a partir de hoje. |
| RN17 | A senha não pode ser formada só por espaços. |
| RN18 | Na busca por descrição, `%` e `_` valem como texto comum (não são curinga). |
| RN19 | Repetição mensal: de 1 a 60 meses; dia 31 em mês curto vira o último dia do mês; tudo é validado antes (ou grava todos ou nenhum). |
| RN20 | Exclusão em lote só atinge lançamentos do próprio usuário; ids inválidos ou de outro usuário são ignorados. |

## 1.6 Requisitos não funcionais
| ID | Requisito | Como é atendido |
|---|---|---|
| RNF01 | Usabilidade: interface simples, clara e consistente | Princípios de Norman/IHC (ver `04-ihc.md`) |
| RNF02 | Confiabilidade: erros tratados com mensagem amigável | Validação no model + mensagens + página 404 |
| RNF03 | Testabilidade | 166 testes automatizados com pytest |
| RNF04 | Manutenibilidade | Arquitetura MVC com Blueprints e pastas separadas (backend, frontend, database) |
| RNF05 | Portabilidade | SQLite (dev) e PostgreSQL (produção) via SQLAlchemy |
| RNF06 | Responsividade | Cabeçalho fixo e compacto, cartões do resumo na mesma linha e tabelas em formato de cartão no celular, sem rolagem horizontal |
| RNF07 | Segurança básica | Consultas parametrizadas (ORM), escape automático no Jinja2, ações que alteram dados (inclusive logout) só via POST, senha com hash, cookie de sessão `HttpOnly` + `SameSite=Lax` (e `Secure` no Render), `session.clear()` ao logar, sem redirecionamento aberto, telas internas com `Cache-Control: no-store` (o botão Voltar não mostra dados após sair), CSV protegido contra fórmulas de planilha |
