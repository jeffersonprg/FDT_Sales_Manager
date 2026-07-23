# Modelagem do Sistema

## Cliente

Descrição:
Representa uma pessoa ou empresa que realizou compras.

### Campos

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

Representa um produto ou serviço comercializado pela FDT.

Os produtos podem ter diferentes regras de validade de acesso. Por exemplo:

- Acesso temporário, como 3, 6 ou 12 meses;
- Acesso vitalício, sem data de expiração.

### Campos

- id
- nome
- categoria
- preco
- descricao
- tipo_validade
- duracao_dias
- ativo

### Tipo de validade

O campo `tipo_validade` poderá assumir, inicialmente, os seguintes valores:

- `TEMPORARIO`
- `VITALICIO`

### Duração

O campo `duracao_dias` será utilizado quando o produto possuir validade temporária.

Exemplos:

| Produto | Tipo de validade | Duração |
|---|---|---:|
| Curso de Python | TEMPORARIO | 365 dias |
| Mentoria | TEMPORARIO | 90 dias |
| Curso Premium | VITALICIO | Não aplicável |

Para produtos vitalícios, `duracao_dias` poderá ser `NULL`.

---

## ItemPedido

Representa um produto específico incluído em um pedido.

Além das informações comerciais da compra, armazena o período efetivo de acesso adquirido pelo cliente.

### Campos

- id
- pedido_id
- produto_id
- quantidade
- preco_unitario
- subtotal
- inicio_acesso
- fim_acesso

### Datas de acesso

O período de acesso é registrado no momento da compra.

Exemplo:

Produto:

Curso de Python

Validade:

365 dias

Compra:

01/08/2026

Resultado:

- inicio_acesso: 01/08/2026
- fim_acesso: 01/08/2027

Para produtos vitalícios:

- inicio_acesso: data da compra
- fim_acesso: NULL

---

## Lead

Representa um potencial cliente.

### Campos

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