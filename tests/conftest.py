from pathlib import Path
from uuid import uuid4

import pytest

from src.database import database


PASTA_BANCOS_TESTE = (
    Path(__file__).resolve().parent / "_temp_databases"
)


@pytest.fixture
def banco_temporario(monkeypatch):
    """
    Cria uma base SQLite isolada para cada teste.
    """

    PASTA_BANCOS_TESTE.mkdir(
        parents=True,
        exist_ok=True
    )

    caminho_banco = (
        PASTA_BANCOS_TESTE
        / f"teste_{uuid4().hex}.db"
    ).resolve()

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        caminho_banco
    )

    database.create_tables()

    try:
        yield caminho_banco
    finally:
        caminho_banco.unlink(missing_ok=True)