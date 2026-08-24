# Modelagem do Sistema

## Cliente

Representa uma pessoa ou empresa relacionada ao MiniCRM.

Campos: `id`, `nome`, `empresa`, `morada`, `telefone`, `email`, `pais`,
`tipo_documento`, `numero_documento`, `estado`, `observacoes`, `criado_em` e
`atualizado_em`.

O estado pode ser `ATIVO` ou `INATIVO`. A remoção normal é lógica.

## Produto

Representa um produto ou serviço comercializado.

Campos: `id`, `nome`, `categoria`, `preco`, `descricao`, `tipo_validade`,
`duracao_dias` e `ativo`.

`tipo_validade` aceita `TEMPORARIO` ou `VITALICIO`. Produtos temporários exigem
uma duração positiva; produtos vitalícios não possuem duração em dias.

## Pedido

Representa uma operação comercial de um cliente.

Campos: `id`, `cliente_id`, `referencia_externa`, `data_pedido`, `estado`,
`total`, `observacoes`, `pago_em`, `cancelado_em`, `criado_em` e
`atualizado_em`.

Estados: `PENDENTE`, `PAGO` e `CANCELADO`. Apenas pedidos pagos compõem a
faturação e concedem acesso.

## ItemPedido

Representa um produto incluído no pedido.

Campos: `id`, `pedido_id`, `produto_id`, `quantidade`, `preco_unitario`,
`subtotal`, `inicio_acesso` e `fim_acesso`.

O preço unitário é o valor negociado na venda. O período de acesso é definido
no pagamento. Para validade vitalícia, `fim_acesso` é nulo.

## Lead

Representa um potencial cliente.

Campos: `id`, `nome`, `empresa`, `telefone`, `email`, `origem`, `estado`,
`produto_interesse_id`, `cliente_id`, `observacoes`, `convertido_em`,
`criado_em` e `atualizado_em`.

Estados: `NOVO`, `CONTACTADO`, `QUALIFICADO`, `CONVERTIDO` e `PERDIDO`.

## Relações

- Cliente 1:N Pedido
- Pedido 1:N ItemPedido
- Produto 1:N ItemPedido
- Produto 1:N Lead como interesse opcional
- Cliente 1:N Lead convertido
