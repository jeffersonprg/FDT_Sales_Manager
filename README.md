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
- migrações incrementais do banco de dados.

Próximas etapas:

1. integrar a importação CSV ao MiniCRM;
2. gerar relatórios HTML;
3. construir a interface gráfica.

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

Estado atual: **129 testes aprovados**.
