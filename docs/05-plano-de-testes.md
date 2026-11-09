# 5. Plano de Testes (Verificação e Validação)

## 5.1 Verificação x Validação
- **Verificação** (estamos construindo certo?): revisão do código e testes automatizados com pytest.
- **Validação** (construímos o produto certo?): teste feito por 5 colegas usando o sistema de verdade.

Relação com o Modelo V:
| Desenvolvimento | Teste correspondente neste projeto |
|---|---|
| Requisitos | Teste de aceitação: colegas usando a solução |
| Arquitetura | Teste de sistema: fluxo completo pela interface |
| Projeto detalhado | Teste de integração: `backend/tests/test_rotas.py` (controller + model + banco) |
| Código | Teste unitário: `backend/tests/test_models.py` |

## 5.2 Testes automatizados
Execute com `cd backend && python -m pytest -v`. Resultado atual: **59 testes, todos passando**.

| Arquivo | O que cobre |
|---|---|
| `backend/tests/test_models.py` | RN01–RN08: validações de valor, descrição, data e categoria; duplicidade; exclusão bloqueada; resumo mensal |
| `backend/tests/test_rotas.py` | Fluxos completos (com usuário logado): criar, editar, excluir, filtros, busca, erros e 404 |
| `backend/tests/test_auth.py` | RF08–RF11 e RN09–RN13: cadastro (ok, e-mail duplicado sem diferenciar maiúsculas, senha curta, senhas diferentes), login ok/errado, rotas protegidas, logout só por POST e isolamento (usuário B não vê, edita nem exclui dados do A; categorias separadas por usuário) |

## 5.3 Casos de teste manuais (para os colegas)
| ID | Cenário | Passos | Resultado esperado |
|---|---|---|---|
| CT01 | Criar receita | Novo lançamento → categoria "Salário" → valor 3000 | Aparece na lista com "+" e entra nas receitas do resumo |
| CT02 | Criar despesa com vírgula | Valor `45,90` | Valor salvo como R$ 45,90 |
| CT03 | Valor negativo | Valor `-10` | Erro "O valor deve ser maior que zero" e dados mantidos |
| CT04 | Descrição vazia | Deixar em branco | Erro "A descrição é obrigatória" |
| CT05 | Editar lançamento | Lista → Editar → mudar valor | Lista e resumo atualizados |
| CT06 | Excluir lançamento | Excluir → confirmar | Lançamento some; saldo recalculado |
| CT07 | Cancelar exclusão | Excluir → cancelar no aviso | Nada é excluído |
| CT08 | Nova categoria | Categorias → Nova | Aparece na lista e no formulário de lançamentos |
| CT09 | Categoria duplicada | Criar "lazer" | Erro "Já existe uma categoria com esse nome" |
| CT10 | Excluir categoria em uso | Excluir categoria com lançamentos | Bloqueado com mensagem |
| CT11 | Filtros e busca | Filtrar por tipo, categoria e descrição | Lista mostra só o que combina |
| CT12 | Navegar entre meses | Anterior / Próximo | Resumo muda para o mês escolhido |
| CT13 | Celular | Abrir no celular | Layout legível, sem rolagem horizontal |
| CT14 | Endereço inexistente | Entrar e abrir `/lancamentos/9999/editar` | Página "Página não encontrada" |
| CT15 | Cadastro ok | Criar conta com dados válidos | Entra logado, nome no menu, 7 categorias padrão |
| CT16 | E-mail repetido | Cadastrar de novo com o mesmo e-mail (tente em maiúsculas) | Erro "Já existe uma conta com esse e-mail." |
| CT17 | Senha curta | Senha com 5 caracteres | Erro "A senha deve ter no mínimo 6 caracteres." |
| CT18 | Senhas diferentes | Confirmação diferente da senha | Erro "A confirmação de senha não confere." e nome/e-mail mantidos |
| CT19 | Login errado | E-mail ou senha incorretos | "E-mail ou senha incorretos." |
| CT20 | Acesso sem login | Sem entrar, abrir `/` ou `/lancamentos/` | Vai direto para a tela de login, sem mensagem de erro |
| CT21 | Sair | Clicar em "Sair" e tentar abrir o resumo | Sessão encerrada; pede login |
| CT22 | Isolamento | Com 2 contas (A e B): A cria lançamento; B abre a lista e tenta o endereço de edição do lançamento do A | B não vê nada de A; o endereço retorna "Página não encontrada" |
