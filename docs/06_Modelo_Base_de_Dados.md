## Modelo da Base de Dados
- Tabela: clientes

Campo	    Tipo        SQLite	        Restrições
id	        INTEGER	    PRIMARY KEY     AUTOINCREMENT
nome	    TEXT	    NOT NULL
morada	    TEXT	    NOT NULL
telefone	TEXT	
email	    TEXT	
nif	        TEXT	
observacoes	TEXT	
criado_em	TEXT	    NOT NULL


- Tabela: produtos

Campo	        Tipo        SQLite	        Restrições
id	            INTEGER	    PRIMARY KEY     AUTOINCREMENT
nome	        TEXT	    NOT NULL
categoria	    TEXT	
preco	        REAL	    NOT NULL
descricao	    TEXT
tipo_validade	TEXT	    NOT NULL
duracao_dias	INTEGER	
ativo	        INTEGER	    DEFAULT 1




- Tabela: pedidos

Um pedido representa uma venda.

Ele pertence a um cliente, mas pode conter vários produtos.

Campo	    Tipo
id	        INTEGER
cliente_id	INTEGER
data	    TEXT
estado	    TEXT
total	    REAL


- Tabela: itens_pedido

Esta tabela liga Pedidos e Produtos.

Campo	            Tipo        Restrições
id	                INTEGER     PRIMARY KEY AUTOINCREMENT
pedido_id	        INTEGER     FOREIGN KEY
produto_id	        INTEGER     FOREIGN KEY
quantidade	        INTEGER     NOT NULL
preco_unitario	    REAL        NOT NULL
subtotal	        REAL        NOT NULL
inicio_acesso	    TEXT	    NOT NULL
fim_acesso	        TEXT


- Tabela: leads
Campo	        Tipo
id	            INTEGER
nome	        TEXT
telefone	    TEXT
email	        TEXT
origem	        TEXT
estado	        TEXT
observacoes 	TEXT

___________
CLIENTES

id

↓

PEDIDOS

cliente_id

↓

ITENS_PEDIDO

pedido_id

↓

PRODUTOS

produto_id

___
## Chaves estrangeiras

- Pedido
cliente_id

↓

clientes.id

- Item Pedido
pedido_id

↓

pedidos.id

- Produto
produto_id

↓

produtos.id


_______

## Fluxo do sistema

Cliente

↓

Novo Pedido

↓

Adicionar Produtos

↓

Calcular Total

↓

Guardar Pedido

↓

Atualizar Dashboard

↓

Relatório HTML