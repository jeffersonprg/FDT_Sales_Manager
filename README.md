# FDT Sales Manager

Aplicação desktop em Python para análise de vendas e gestão comercial da FDT.

## Tecnologias

- Python 3.13
- SQLite
- pytest
- Pandas
- Jinja2
- Matplotlib
- CustomTkinter

## Estado do projeto

O backend do MiniCRM está concluído e coberto por testes automatizados:

- clientes com desativação lógica;
- produtos temporários e vitalícios;
- leads e conversão transacional em clientes;
- pedidos, pagamento e cancelamento;
- controlo de acessos iniciado na data do pagamento;
- faturação comercial;
- dashboard e estatísticas de vendas;
- importação CSV transacional e idempotente;
- relatórios HTML autônomos com indicadores, tabelas e gráficos;
- interface gráfica com navegação, dashboard e consultas comerciais;
- migrações incrementais do banco de dados.

Próxima etapa: completar o fluxo visual de pedidos, incluindo itens, pagamento
e cancelamento.

## Preparação do ambiente

No Windows, com Python 3.13 instalado:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

O ambiente `venv` antigo não deve ser reutilizado quando apontar para uma
instalação de Python removida; recrie-o como `.venv` com os comandos acima.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Estado atual: **151 testes aprovados**.

## Interface gráfica

```powershell
.\.venv\Scripts\python.exe app.py
```

A aplicação abre no dashboard e oferece navegação para clientes, produtos,
leads, pedidos, importação CSV e relatórios. As listas permitem pesquisa e são
atualizadas diretamente a partir dos serviços do MiniCRM. Clientes e produtos
já possuem formulários de criação e edição, além de ativação e inativação com
preservação do histórico. Leads também podem ser criados, editados, movidos no
funil e convertidos transacionalmente em clientes.

## Importação CSV

O formato atual usa as colunas `data`, `nome_cliente`, `morada`,
`informacao_cliente`, `pedido`, `produto`, `quantidade`, `preco_unitario` e
`faturacao`.

```powershell
.\.venv\Scripts\python.exe -m src.csv_reader `
    src\data\imports\vendas_exemplo.csv
```

Novos produtos são vitalícios por padrão. Para importar produtos temporários:

```powershell
.\.venv\Scripts\python.exe -m src.csv_reader vendas.csv `
    --tipo-validade TEMPORARIO --duracao-dias 30
```

A operação é atômica, registra o hash do arquivo e ignora referências de pedido
que já existam.

## Relatório HTML

O relatório comercial é gerado a partir dos dados atuais do MiniCRM e reúne
indicadores, faturação mensal, vendas por produto, pedidos pagos e histórico de
importações. O arquivo é autônomo: estilos e gráficos SVG ficam incorporados no
próprio HTML.

```powershell
.\.venv\Scripts\python.exe -m src.report_generator `
    --saida src\data\reports\relatorio_comercial.html
```

Também é possível limitar o período com `--inicio AAAA-MM-DD` e
`--fim AAAA-MM-DD`.
