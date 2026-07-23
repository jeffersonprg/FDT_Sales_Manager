# Diagrama Entidade-Relacionamento (ERD)

## Objetivo

Representar visualmente as entidades do sistema e os seus relacionamentos antes da implementação da base de dados.

```mermaid
erDiagram

    CLIENTE ||--o{ PEDIDO : realiza
    PEDIDO ||--|{ ITEM_PEDIDO : contem
    PRODUTO ||--o{ ITEM_PEDIDO : incluido_em
    CLIENTE o|--o{ LEAD : originou

    CLIENTE {
        int id PK
        string nome
        string morada
        string telefone
        string email
        string nif
        string observacoes
        datetime criado_em
    }

    PRODUTO {
        int id PK
        string nome
        string categoria
        decimal preco
        string descricao
        string tipo_validade
        int duracao_dias
        boolean ativo
    }

    PEDIDO {
        int id PK
        int cliente_id FK
        datetime data
        string estado
        decimal total
    }

    ITEM_PEDIDO {
        int id PK
        int pedido_id FK
        int produto_id FK
        int quantidade
        decimal preco_unitario
        decimal subtotal
        date inicio_acesso
        date fim_acesso
    }

    LEAD {
        int id PK
        string nome
        string telefone
        string email
        string origem
        string estado
        int cliente_id FK
        string observacoes
    }
```

## Regra de validade dos produtos

Um produto pode possuir:

### Validade temporária

```text
tipo_validade: TEMPORARIO
duracao_dias: 365
```

O sistema calcula:

```text
fim_acesso = inicio_acesso + duracao_dias
```

### Acesso vitalício

```text
tipo_validade: VITALICIO
duracao_dias: NULL
fim_acesso: NULL
```

As datas efetivas de acesso são armazenadas em `ITEM_PEDIDO`, pois representam a aquisição específica realizada pelo cliente.