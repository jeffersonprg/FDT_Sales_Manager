# Modelagem do Sistema

## Cliente

Descrição:
Representa uma pessoa ou empresa que realizou compras.

Campos:

- id
- nome
- morada
- telefone
- email
- nif
- observacoes
- criado_em

---

## Produto

Representa um produto vendido.

Campos:

- id
- nome
- categoria
- preco
- descricao
- ativo

---

## Pedido

Representa uma venda.

Campos:

- id
- cliente_id
- produto_id
- quantidade
- valor_total
- data
- estado

---

## Lead

Representa um potencial cliente.

Campos:

- id
- nome
- telefone
- email
- origem
- estado
- observacoes

---

## Relações

Cliente 1:N Pedido

Produto 1:N Pedido

Lead -> Cliente