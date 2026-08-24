import pandas as pd

from utils.validator import (
    validar_colunas,
    validar_valores_ausentes,
    validar_valores_negativos,
    validar_faturacao
)


caminho_csv = "src/data/imports/vendas_exemplo.csv"

dados = pd.read_csv(caminho_csv)

dados["data"] = pd.to_datetime(dados["data"])


validar_colunas(dados)

validar_valores_ausentes(dados)

validar_valores_negativos(dados)

validar_faturacao(dados)