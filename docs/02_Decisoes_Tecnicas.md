# Decisões Técnicas

## Plataforma

- Linguagem: Python 3.13
- Interface: CustomTkinter
- Banco de dados: SQLite
- Leitura e análise de CSV: Pandas
- Gráficos: Matplotlib
- Relatórios: Jinja2 + HTML
- Imagens: Pillow
- Testes: pytest

## Arquitetura

O projeto utiliza uma arquitetura modular:

- `database`: conexão, criação do esquema e migrações;
- `models`: entidades e validações de domínio;
- `services`: operações, transações e consultas comerciais;
- `views`: interface gráfica;
- `utils`: validações e utilidades compartilhadas.

## Regras de persistência

- Todas as conexões são fechadas em blocos `finally`.
- Escritas compostas utilizam transações com rollback.
- Migrações são incrementais e registradas em `schema_migrations`.
- E-mails, documentos, nomes de produtos e referências externas possuem
  unicidade sem diferenciação entre maiúsculas e minúsculas.
- Clientes e produtos são desativados logicamente para preservar histórico.
- Datas internas são serializadas em ISO 8601 e tratadas como UTC sem
  informação de fuso no SQLite.
- Valores monetários são arredondados para duas casas decimais.

## Regras comerciais

- O preço do item representa o preço efetivamente negociado e pode diferir do
  preço atual do catálogo.
- Apenas pedidos pagos integram a faturação.
- O acesso ao produto começa no pagamento, não na criação do pedido.
- Um produto temporário com duração de `N` dias fica ativo por exatamente `N`
  datas de calendário, incluindo a data inicial.
- Pedidos aceitam as transições `PENDENTE -> PAGO`,
  `PENDENTE -> CANCELADO` e `PAGO -> CANCELADO`.
- Pedidos cancelados são terminais e deixam de conceder acesso ou faturação.

## Testes automatizados

Os testes ficam em `tests/` e utilizam um banco SQLite isolado por teste.
O estado atual é de 129 testes aprovados.
