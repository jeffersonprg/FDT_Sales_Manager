import pandas as pd


caminho_csv = "src/data/imports/vendas_exemplo.csv"

dados = pd.read_csv(caminho_csv)

dados["data"] = pd.to_datetime(dados["data"])


colunas_obrigatorias = [
    "data",
    "nome_cliente",
    "morada",
    "informacao_cliente",
    "pedido",
    "produto",
    "quantidade",
    "preco_unitario",
    "faturacao"
]

colunas_em_falta = [
    coluna
    for coluna in colunas_obrigatorias
    if coluna not in dados.columns
]

if colunas_em_falta:
    print("ERRO: Existem colunas obrigatórias em falta:")
    print(colunas_em_falta)
else:
    print("Validação das colunas concluída com sucesso.")

print("=== PRIMEIRAS LINHAS ===")
print(dados.head())


print("\n=== DIMENSÃO DOS DADOS ===")
print(f"Linhas: {dados.shape[0]}")
print(f"Colunas: {dados.shape[1]}")


print("\n=== NOMES DAS COLUNAS ===")
print(dados.columns.tolist())


print("\n=== TIPOS DE DADOS ===")
print(dados.dtypes)

valores_ausentes = dados.isnull().sum()

print("\n=== VALORES AUSENTES ===")
print(valores_ausentes)