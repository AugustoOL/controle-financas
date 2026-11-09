# 4. Interface Humano-Computador (IHC)

## 4.1 Mapa de navegação
```mermaid
flowchart TD
    R[Resumo do mês /] --> L[Lançamentos /lancamentos]
    R --> C[Categorias /categorias]
    R --> NL[Novo lançamento]
    L --> NL
    L --> EL[Editar lançamento]
    C --> NC[Nova categoria]
    C --> EC[Editar categoria]
```
Todas as telas têm o mesmo menu no topo (Resumo, Lançamentos, Categorias).

## 4.2 Telas
| Tela | Objetivo | Imagem |
|---|---|---|
| Resumo | Ver receitas, despesas, saldo, total por categoria e últimos lançamentos do mês | `img/dashboard.png` |
| Lançamentos | Listar, buscar, filtrar, editar e excluir | `img/lancamentos.png` |
| Novo/Editar lançamento | Formulário com validação | `img/novo_lancamento.png` |
| Categorias | Gerenciar categorias | `img/categorias.png` |

## 4.3 Princípios de IHC aplicados
| Princípio | Como foi aplicado |
|---|---|
| Clareza | Rótulos diretos ("Valor (R$)", "Salvar"); receitas em verde e despesas em vermelho, sempre com texto e sinal (+/−), sem depender só da cor |
| Consistência | Mesmo menu, botões e estilo de tabela e formulário em todas as telas |
| Simplicidade | Formulário com poucos campos; observação é opcional |
| Controle do usuário | O usuário decide o mês, os filtros e quando salvar; sempre há "Cancelar" |
| Resposta (feedback) | Mensagem de sucesso ou erro a cada ação |
| Recuperabilidade | Confirmação antes de excluir; o formulário com erro mantém o que foi digitado |
| Acessibilidade | Labels associados aos campos, foco visível, contraste adequado, layout responsivo |
| Padrões | Data em formato brasileiro (dd/mm/aaaa) e valores em R$ 1.234,56 |

## 4.4 Mensagens de erro e de sucesso
| Situação | Mensagem |
|---|---|
| Descrição vazia | "A descrição é obrigatória." |
| Valor inválido | "Informe um valor numérico válido." |
| Valor ≤ 0 | "O valor deve ser maior que zero." |
| Data inválida | "Informe uma data válida." |
| Categoria não escolhida | "Selecione uma categoria válida." |
| Categoria repetida | "Já existe uma categoria com esse nome." |
| Excluir categoria em uso | "Não é possível excluir: existem lançamentos nesta categoria." |
| Página inexistente | Tela "Página não encontrada" com botão para voltar ao início |
| Sucesso | "Lançamento registrado com sucesso.", "Categoria criada com sucesso." etc. |
