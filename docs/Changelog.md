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

## [Importação CSV integrada] — 24/08/2026

### Adicionado

- Serviço transacional de importação CSV.
- Agrupamento de várias linhas por referência de pedido.
- Criação e reutilização de clientes e produtos.
- Criação de pedidos pagos, itens e períodos de acesso.
- Histórico de importações com hash SHA-256.
- Prevenção de duplicações por arquivo e referência externa.
- Resumo estruturado com registros criados, reutilizados e ignorados.
- Suporte a novos produtos vitalícios ou temporários.
- Interface de linha de comando através de `python -m src.csv_reader`.

### Validações

- Colunas e valores obrigatórios.
- Datas e números válidos.
- Quantidades inteiras e positivas.
- Faturação igual a quantidade multiplicada pelo preço unitário.
- Consistência de cliente e data entre linhas do mesmo pedido.
- Preço consistente quando um produto se repete no pedido.

### Testes

- 137 testes automatizados aprovados.

## [Relatório HTML integrado] — 24/08/2026

### Adicionado

- Serviço de geração de relatório comercial a partir dos dados do MiniCRM.
- Indicadores de clientes, produtos, leads, pedidos, faturação e ticket médio.
- Tabelas de vendas por produto, pedidos pagos e histórico de importações CSV.
- Gráficos SVG incorporados de faturação mensal e desempenho por produto.
- Filtros opcionais de data e estados vazios para bases sem vendas.
- Template responsivo e preparado para impressão.
- Interface de linha de comando através de `python -m src.report_generator`.
- Relatório da base atual e relatório demonstrativo gerados para validação.

### Testes

- 143 testes automatizados aprovados.

## [Fundação da interface gráfica] — 25/08/2026

### Adicionado

- Janela principal em CustomTkinter com navegação lateral por módulos.
- Dashboard conectado aos indicadores e últimos pedidos do MiniCRM.
- Cartões de faturação, ticket médio, clientes, produtos, leads e pedidos.
- Telas pesquisáveis para clientes, produtos, leads e pedidos.
- Interface de seleção e importação de vendas CSV.
- Interface de geração de relatórios HTML com filtro por período.
- Componentes visuais reutilizáveis para cabeçalhos, tabelas, cartões e avisos.
- Camada de apresentação independente de Tk para formatação e testes.

### Alterado

- `app.py` passa a inicializar o banco e abrir a aplicação gráfica.
- Dependências específicas de CSV e relatório passam a ser carregadas sob
  demanda na interface.

### Testes

- 148 testes automatizados aprovados.

## [CRUD visual de clientes e produtos] — 25/08/2026

### Adicionado

- Modal reutilizável para formulários com campos de texto, seleção e descrição.
- Criação e edição de clientes pela interface.
- Ativação e inativação de clientes sem exclusão do histórico.
- Criação e edição de produtos vitalícios e temporários.
- Ativação e inativação de produtos sem exclusão do histórico.
- Edição por botão ou duplo clique na linha selecionada.
- Conversores testáveis para preços, inteiros e campos opcionais.
- Mensagens de sucesso, seleção obrigatória e erros de validação nos formulários.

### Testes

- 150 testes automatizados aprovados.

## [CRUD visual e conversão de leads] — 26/08/2026

### Adicionado

- Criação e edição de leads pela interface gráfica.
- Seleção do estado do funil entre novo, contactado, qualificado e perdido.
- Seleção de produto de interesse pelo nome, mantendo o ID no domínio.
- Exibição do produto de interesse na tabela de leads.
- Conversão visual e transacional de lead em cliente.
- Formulário de conversão com morada, país, documento e observações.
- Proteção contra edição ou reconversão de leads já convertidos.
- Conversores testáveis entre opções visuais e IDs das entidades.

### Testes

- 151 testes automatizados aprovados.

## [Fluxo visual de pedidos] — 26/08/2026

### Adicionado

- Criação visual de pedidos para clientes ativos.
- Composição de pedidos com vários produtos, quantidades e preços negociados.
- Cálculo e apresentação do total antes da gravação.
- Remoção de itens durante a montagem do pedido.
- Consulta detalhada dos produtos e períodos de acesso.
- Registo de pagamento com data opcional.
- Cancelamento de pedidos pendentes ou pagos.
- Proteção visual das transições de estado não permitidas.
- Pesquisa de pedidos por ID, referência ou nome do cliente.
- Comentários e docstrings nos módulos visuais para explicar responsabilidades
  e decisões menos evidentes.

### Testes

- 152 testes automatizados aprovados.
