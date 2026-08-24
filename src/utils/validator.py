def validar_colunas(dados):
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
        return False

    print("Validação das colunas concluída com sucesso.")
    return True

def validar_valores_ausentes(dados):
    valores_ausentes = dados.isnull().sum()

    print("\n=== VALORES AUSENTES ===")
    print(valores_ausentes)

    return valores_ausentes.sum() == 0

def validar_valores_negativos(dados):
    quantidades_negativas = (dados["quantidade"] < 0).sum()
    precos_negativos = (dados["preco_unitario"] < 0).sum()
    faturacoes_negativas = (dados["faturacao"] < 0).sum()

    print("\n=== VALIDAÇÃO DE VALORES NEGATIVOS ===")
    print(f"Quantidades negativas: {quantidades_negativas}")
    print(f"Preços negativos: {precos_negativos}")
    print(f"Faturações negativas: {faturacoes_negativas}")

    return (
        quantidades_negativas == 0
        and precos_negativos == 0
        and faturacoes_negativas == 0
    )

def validar_faturacao(dados):
    dados["faturacao_calculada"] = (
        dados["quantidade"] * dados["preco_unitario"]
    )

    dados["faturacao_consistente"] = (
        dados["faturacao_calculada"] == dados["faturacao"]
    )

    print("\n=== VALIDAÇÃO DA FATURAÇÃO ===")
    print(dados["faturacao_consistente"].value_counts())

    return dados["faturacao_consistente"].all()

