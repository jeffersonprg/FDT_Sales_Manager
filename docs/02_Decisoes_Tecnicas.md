# Decisões Técnicas

## Plataforma

- Linguagem: Python 3.13
- Interface: CustomTkinter
- Banco de dados: SQLite
- Leitura e análise de CSV: Pandas
- Gráficos: Matplotlib
- Relatórios: Jinja2 + HTML com gráficos SVG incorporados
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
O estado atual é de 152 testes aprovados.

## Arquitetura da interface

- A janela principal mantém a navegação e carrega cada tela sob demanda.
- Componentes comuns de cabeçalho, indicadores, tabelas e mensagens ficam em
  `src/views/components.py`.
- Formatação e montagem dos dados visuais ficam em `src/presentation.py`, sem
  dependência de Tk, permitindo testes automatizados rápidos.
- As telas consultam os serviços existentes e não duplicam regras comerciais.
- Pandas e Jinja2 são carregados somente quando a importação ou a geração de
  relatório é executada, reduzindo o acoplamento do arranque da aplicação.

## Contrato de importação CSV

- Cada referência da coluna `pedido` representa um pedido.
- Linhas com a mesma referência são agrupadas no mesmo pedido.
- Clientes são reutilizados pela combinação normalizada de nome e morada.
- Produtos são reutilizados pelo nome sem diferenciação de caixa.
- O preço do item vem do CSV; o preço inicial do catálogo vem da primeira venda.
- Novos produtos são vitalícios por padrão, com opção de validade temporária.
- Vendas importadas entram como pagas na data da coluna `data`.
- A importação inteira usa uma transação e rollback em qualquer erro.
- O SHA-256 do arquivo é registrado para impedir reprocessamento idêntico.
- Referências externas já existentes são ignoradas e incluídas no resumo.

## Contrato do relatório HTML

- Os dados são consultados diretamente nos serviços do MiniCRM.
- Filtros opcionais de data afetam faturação, série mensal e pedidos listados.
- Indicadores gerais, vendas por produto e histórico de importações são
  apresentados no mesmo documento.
- Os gráficos são SVG incorporados como `data:` URLs, sem dependência de rede
  ou de arquivos de imagem externos.
- A saída é gravada de forma atômica para evitar relatórios incompletos.
- Valores e textos inseridos no template recebem formatação e escape de HTML.
