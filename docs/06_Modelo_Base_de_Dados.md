# Modelo da Base de Dados

## clientes

| Campo | Tipo | Regras principais |
|---|---|---|
| id | INTEGER | PK, autoincremento |
| nome | TEXT | obrigatório, não vazio |
| empresa | TEXT | opcional |
| morada | TEXT | opcional |
| telefone | TEXT | opcional |
| email | TEXT | opcional, único sem diferenciar caixa |
| pais | TEXT | obrigatório, padrão `Portugal` |
| tipo_documento | TEXT | opcional |
| numero_documento | TEXT | opcional, único sem diferenciar caixa |
| estado | TEXT | `ATIVO` ou `INATIVO` |
| observacoes | TEXT | opcional |
| criado_em | TIMESTAMP | preenchimento automático |
| atualizado_em | TIMESTAMP | preenchimento automático |

## produtos

| Campo | Tipo | Regras principais |
|---|---|---|
| id | INTEGER | PK, autoincremento |
| nome | TEXT | obrigatório e único sem diferenciar caixa |
| categoria | TEXT | opcional |
| preco | REAL | maior ou igual a zero |
| descricao | TEXT | opcional |
| tipo_validade | TEXT | `TEMPORARIO` ou `VITALICIO` |
| duracao_dias | INTEGER | positivo apenas para temporários |
| ativo | INTEGER | `0` ou `1` |

## pedidos

| Campo | Tipo | Regras principais |
|---|---|---|
| id | INTEGER | PK, autoincremento |
| cliente_id | INTEGER | FK para clientes, exclusão restrita |
| referencia_externa | TEXT | opcional e única sem diferenciar caixa |
| data_pedido | TIMESTAMP | obrigatória |
| estado | TEXT | `PENDENTE`, `PAGO` ou `CANCELADO` |
| total | REAL | maior ou igual a zero |
| observacoes | TEXT | opcional |
| pago_em | TIMESTAMP | obrigatório quando pago |
| cancelado_em | TIMESTAMP | preenchido no cancelamento |
| criado_em | TIMESTAMP | preenchimento automático |
| atualizado_em | TIMESTAMP | preenchimento automático |

## itens_pedido

| Campo | Tipo | Regras principais |
|---|---|---|
| id | INTEGER | PK, autoincremento |
| pedido_id | INTEGER | FK para pedidos, exclusão em cascata |
| produto_id | INTEGER | FK para produtos, exclusão restrita |
| quantidade | INTEGER | maior que zero |
| preco_unitario | REAL | maior ou igual a zero |
| subtotal | REAL | maior ou igual a zero |
| inicio_acesso | DATE | definido no pagamento |
| fim_acesso | DATE | opcional; nunca anterior ao início |

Cada produto só pode aparecer uma vez por pedido.

## leads

| Campo | Tipo | Regras principais |
|---|---|---|
| id | INTEGER | PK, autoincremento |
| nome | TEXT | obrigatório e não vazio |
| empresa, telefone, email, origem | TEXT | opcionais |
| estado | TEXT | estado válido do funil |
| produto_interesse_id | INTEGER | FK opcional para produtos |
| cliente_id | INTEGER | FK preenchida após conversão |
| observacoes | TEXT | opcional |
| convertido_em | TIMESTAMP | obrigatório quando convertido |
| criado_em, atualizado_em | TIMESTAMP | preenchimento automático |

## schema_migrations

Registra cada versão de migração aplicada, garantindo idempotência e evolução
segura da base existente.
