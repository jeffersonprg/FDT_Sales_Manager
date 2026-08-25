from collections.abc import Iterable

import pandas as pd


COLUNAS_OBRIGATORIAS = (
    "data",
    "nome_cliente",
    "morada",
    "informacao_cliente",
    "pedido",
    "produto",
    "quantidade",
    "preco_unitario",
    "faturacao",
)

COLUNAS_TEXTO = (
    "nome_cliente",
    "morada",
    "informacao_cliente",
    "pedido",
    "produto",
)


def validar_colunas(dados: pd.DataFrame) -> bool:
    return all(coluna in dados.columns for coluna in COLUNAS_OBRIGATORIAS)


def colunas_em_falta(dados: pd.DataFrame) -> list[str]:
    return [
        coluna
        for coluna in COLUNAS_OBRIGATORIAS
        if coluna not in dados.columns
    ]


def validar_valores_ausentes(dados: pd.DataFrame) -> bool:
    if not validar_colunas(dados):
        return False

    obrigatorios = dados.loc[:, list(COLUNAS_OBRIGATORIAS)]
    if obrigatorios.isnull().any().any():
        return False

    for coluna in COLUNAS_TEXTO:
        if obrigatorios[coluna].astype(str).str.strip().eq("").any():
            return False

    return True


def validar_valores_negativos(dados: pd.DataFrame) -> bool:
    try:
        quantidades = pd.to_numeric(dados["quantidade"], errors="raise")
        precos = pd.to_numeric(dados["preco_unitario"], errors="raise")
        faturacoes = pd.to_numeric(dados["faturacao"], errors="raise")
    except (KeyError, TypeError, ValueError):
        return False

    return bool(
        (quantidades > 0).all()
        and (precos >= 0).all()
        and (faturacoes >= 0).all()
    )


def validar_quantidades_inteiras(dados: pd.DataFrame) -> bool:
    try:
        quantidades = pd.to_numeric(dados["quantidade"], errors="raise")
    except (KeyError, TypeError, ValueError):
        return False

    return bool((quantidades % 1 == 0).all())


def validar_faturacao(dados: pd.DataFrame) -> bool:
    try:
        quantidades = pd.to_numeric(dados["quantidade"], errors="raise")
        precos = pd.to_numeric(dados["preco_unitario"], errors="raise")
        faturacoes = pd.to_numeric(dados["faturacao"], errors="raise")
    except (KeyError, TypeError, ValueError):
        return False

    calculado = (quantidades * precos).round(2)
    informado = faturacoes.round(2)
    return bool(calculado.eq(informado).all())


def _linhas_invalidas(mascara: Iterable[bool]) -> list[int]:
    return [
        indice + 2
        for indice, invalido in enumerate(mascara)
        if invalido
    ]


def preparar_dados_csv(dados: pd.DataFrame) -> pd.DataFrame:
    """Valida, normaliza e devolve uma cópia pronta para importação."""

    faltantes = colunas_em_falta(dados)
    if faltantes:
        raise ValueError(
            "Colunas obrigatórias em falta: " + ", ".join(faltantes)
        )

    normalizados = dados.copy()

    for coluna in COLUNAS_TEXTO:
        normalizados[coluna] = normalizados[coluna].apply(
            lambda valor: valor.strip() if isinstance(valor, str) else valor
        )

    ausentes = normalizados.loc[:, list(COLUNAS_OBRIGATORIAS)].isnull()
    linhas_ausentes = sorted(
        {
            indice + 2
            for indice, row in ausentes.iterrows()
            if row.any()
        }
    )
    linhas_vazias = sorted(
        {
            indice + 2
            for coluna in COLUNAS_TEXTO
            for indice, vazio in enumerate(
                normalizados[coluna].astype(str).str.strip().eq("")
            )
            if vazio
        }
    )
    if linhas_ausentes or linhas_vazias:
        linhas = sorted(set(linhas_ausentes + linhas_vazias))
        raise ValueError(
            "Existem valores obrigatórios vazios nas linhas: "
            + ", ".join(map(str, linhas))
        )

    normalizados["data"] = pd.to_datetime(
        normalizados["data"],
        errors="coerce",
    )
    for coluna in ("quantidade", "preco_unitario", "faturacao"):
        normalizados[coluna] = pd.to_numeric(
            normalizados[coluna],
            errors="coerce",
        )

    invalidos = normalizados[
        ["data", "quantidade", "preco_unitario", "faturacao"]
    ].isnull().any(axis=1)
    if invalidos.any():
        raise ValueError(
            "Datas ou valores numéricos inválidos nas linhas: "
            + ", ".join(map(str, _linhas_invalidas(invalidos)))
        )

    if not validar_quantidades_inteiras(normalizados):
        mascara = normalizados["quantidade"] % 1 != 0
        raise ValueError(
            "A quantidade deve ser inteira nas linhas: "
            + ", ".join(map(str, _linhas_invalidas(mascara)))
        )

    normalizados["quantidade"] = normalizados["quantidade"].astype(int)

    if not validar_valores_negativos(normalizados):
        mascara = (
            (normalizados["quantidade"] <= 0)
            | (normalizados["preco_unitario"] < 0)
            | (normalizados["faturacao"] < 0)
        )
        raise ValueError(
            "Quantidade ou valores negativos nas linhas: "
            + ", ".join(map(str, _linhas_invalidas(mascara)))
        )

    if not validar_faturacao(normalizados):
        mascara = (
            normalizados["quantidade"]
            * normalizados["preco_unitario"]
        ).round(2).ne(normalizados["faturacao"].round(2))
        raise ValueError(
            "Faturação inconsistente nas linhas: "
            + ", ".join(map(str, _linhas_invalidas(mascara)))
        )

    normalizados["preco_unitario"] = normalizados[
        "preco_unitario"
    ].round(2)
    normalizados["faturacao"] = normalizados["faturacao"].round(2)

    return normalizados
