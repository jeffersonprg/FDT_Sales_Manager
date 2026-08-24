# Changelog

## v0.1.0

### Adicionado

- Estrutura inicial do projeto.
- Organização das pastas.
- Documentação inicial.

____

## [Em desenvolvimento] — 03/08/2026

### Adicionado

- CRUD do módulo de clientes.
- Gestão de produtos temporários e vitalícios.
- Desativação lógica de produtos.
- Gestão de pedidos e itens de pedido.
- Cálculo automático de subtotais e totais.
- Controlo transacional na criação de pedidos.
- Gestão e pesquisa de leads.
- Conversão transacional de leads em clientes.
- Cálculo automático do período de acesso aos produtos.
- Consulta de acessos ativos, expirados e vitalícios.
- Indicadores comerciais do dashboard.
- Resumo comercial por cliente.
- Pesquisa de clientes, produtos e leads.
- Testes automatizados com pytest.
- Teste integrado do fluxo completo do MiniCRM.

### Alterado

- Base de dados expandida para suportar clientes, produtos, pedidos, itens de pedido e leads.
- Estrutura de testes reorganizada para a pasta `tests`.
- Datas passam a ser serializadas explicitamente no formato ISO 8601.

### Removido

- Scripts manuais de teste existentes na pasta `src`.

## [Backend estável] — 24/08/2026

### Adicionado

- Estado ativo/inativo e desativação lógica de clientes.
- Reativação de clientes e produtos.
- Datas de pagamento e cancelamento de pedidos.
- Transições controladas entre estados de pedido.
- Início do acesso na data efetiva do pagamento.
- Serviço de faturação comercial com filtros por período.
- Serviço de estatísticas e vendas por produto.
- Produto mais vendido e últimos pedidos no dashboard.
- Migrações incrementais registradas em `schema_migrations`.
- Índices únicos case-insensitive para email, documento, produto e referência.
- Testes de migração, validação, faturação e ciclo de pagamento.

### Alterado

- Modelos e serviços agora revalidam dados antes de persistir.
- Serviços de clientes e produtos usam rollback e fechamento garantido.
- Datas retornadas pelos serviços são convertidas para objetos Python.
- Validade temporária representa exatamente a quantidade cadastrada de dias.
- Total de clientes do dashboard considera apenas clientes ativos.

### Testes

- 129 testes automatizados aprovados.
