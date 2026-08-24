import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from src.database import database
from src.database.database import create_tables, get_connection


def test_criar_tabela_produtos(banco_temporario):
    connection = get_connection()

    tabela = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'produtos'
    """).fetchone()

    colunas = connection.execute("""
        PRAGMA table_info(produtos)
    """).fetchall()

    connection.close()

    assert tabela is not None

    nomes_colunas = {coluna["name"] for coluna in colunas}

    assert nomes_colunas == {
        "id",
        "nome",
        "categoria",
        "preco",
        "descricao",
        "tipo_validade",
        "duracao_dias",
        "ativo"
    }
def test_criar_tabelas_pedidos_e_itens_pedido(
    banco_temporario
):
    connection = get_connection()

    tabelas = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name IN ('pedidos', 'itens_pedido')
    """).fetchall()

    colunas_pedidos = connection.execute("""
        PRAGMA table_info(pedidos)
    """).fetchall()

    colunas_itens = connection.execute("""
        PRAGMA table_info(itens_pedido)
    """).fetchall()

    connection.close()

    nomes_tabelas = {tabela["name"] for tabela in tabelas}

    assert nomes_tabelas == {
        "pedidos",
        "itens_pedido"
    }

    nomes_colunas_pedidos = {
        coluna["name"]
        for coluna in colunas_pedidos
    }

    assert nomes_colunas_pedidos == {
        "id",
        "cliente_id",
        "referencia_externa",
        "data_pedido",
        "estado",
        "total",
        "observacoes",
        "pago_em",
        "cancelado_em",
        "criado_em",
        "atualizado_em"
    }

    nomes_colunas_itens = {
        coluna["name"]
        for coluna in colunas_itens
    }

    assert nomes_colunas_itens == {
        "id",
        "pedido_id",
        "produto_id",
        "quantidade",
        "preco_unitario",
        "subtotal",
        "inicio_acesso",
        "fim_acesso"
    }


def test_pedido_exige_cliente_existente(
    banco_temporario
):
    connection = get_connection()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO pedidos (
                cliente_id,
                estado,
                total
            )
            VALUES (?, ?, ?)
        """, (
            9999,
            "PENDENTE",
            100
        ))

    connection.rollback()
    connection.close()
    
def test_criar_tabela_leads(banco_temporario):
    connection = get_connection()

    tabela = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'leads'
    """).fetchone()

    colunas = connection.execute("""
        PRAGMA table_info(leads)
    """).fetchall()

    connection.close()

    assert tabela is not None

    nomes_colunas = {
        coluna["name"]
        for coluna in colunas
    }

    assert nomes_colunas == {
        "id",
        "nome",
        "empresa",
        "telefone",
        "email",
        "origem",
        "estado",
        "produto_interesse_id",
        "cliente_id",
        "observacoes",
        "convertido_em",
        "criado_em",
        "atualizado_em"
    }


def test_lead_nao_aceita_estado_invalido(
    banco_temporario
):
    connection = get_connection()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO leads (
                nome,
                estado
            )
            VALUES (?, ?)
        """, (
            "Lead inválido",
            "EM_ANALISE"
        ))

    connection.rollback()
    connection.close()


def test_lead_convertido_exige_cliente(
    banco_temporario
):
    connection = get_connection()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO leads (
                nome,
                estado
            )
            VALUES (?, ?)
        """, (
            "Lead convertido sem cliente",
            "CONVERTIDO"
        ))

    connection.rollback()
    connection.close()

def test_referencia_externa_pedido_deve_ser_unica(
    banco_temporario
):
    connection = get_connection()

    cursor = connection.execute("""
        INSERT INTO clientes (nome)
        VALUES (?)
    """, ("Cliente Referência",))

    cliente_id = cursor.lastrowid

    connection.execute("""
        INSERT INTO pedidos (
            cliente_id,
            referencia_externa,
            total
        )
        VALUES (?, ?, ?)
    """, (
        cliente_id,
        "PED-001",
        100
    ))

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO pedidos (
                cliente_id,
                referencia_externa,
                total
            )
            VALUES (?, ?, ?)
        """, (
            cliente_id,
            "PED-001",
            200
        ))

    connection.rollback()
    connection.close()


def test_schema_inclui_estado_e_indices_de_unicidade(banco_temporario):
    connection = get_connection()

    try:
        colunas_clientes = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(clientes)"
            ).fetchall()
        }
        indices = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            ).fetchall()
        }

        assert "estado" in colunas_clientes
        assert "idx_clientes_email_nocase" in indices
        assert "idx_clientes_numero_documento_nocase" in indices
        assert "idx_produtos_nome_nocase" in indices
        assert "idx_pedidos_referencia_externa" in indices
    finally:
        connection.close()


def test_banco_exige_data_em_pedido_pago(banco_temporario):
    connection = get_connection()

    try:
        cliente_id = connection.execute(
            "INSERT INTO clientes (nome) VALUES (?)",
            ("Cliente pagamento",)
        ).lastrowid

        with pytest.raises(
            sqlite3.IntegrityError,
            match="pedido pago exige data de pagamento"
        ):
            connection.execute("""
                INSERT INTO pedidos (cliente_id, estado, total)
                VALUES (?, 'PAGO', 100)
            """, (cliente_id,))
    finally:
        connection.rollback()
        connection.close()


def test_migracao_preserva_cliente_de_schema_anterior(monkeypatch):
    pasta = Path(__file__).resolve().parent / "_temp_databases"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"legacy_{uuid4().hex}.db"

    connection = sqlite3.connect(caminho)
    connection.execute("""
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            empresa TEXT,
            morada TEXT,
            telefone TEXT,
            email TEXT UNIQUE,
            pais TEXT NOT NULL DEFAULT 'Portugal',
            tipo_documento TEXT,
            numero_documento TEXT,
            observacoes TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.execute(
        "INSERT INTO clientes (nome, email) VALUES (?, ?)",
        ("Cliente legado", "LEGADO@EMAIL.PT")
    )
    connection.execute("""
        CREATE TABLE pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data_pedido TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            estado TEXT NOT NULL DEFAULT 'PENDENTE',
            total REAL NOT NULL DEFAULT 0,
            observacoes TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    connection.commit()
    connection.close()

    monkeypatch.setattr(database, "DATABASE_PATH", caminho)

    try:
        create_tables()
        connection = get_connection()
        row = connection.execute(
            "SELECT nome, email, estado FROM clientes"
        ).fetchone()
        versao = connection.execute(
            "SELECT MAX(versao) AS versao FROM schema_migrations"
        ).fetchone()["versao"]
        connection.close()

        assert row["nome"] == "Cliente legado"
        assert row["email"] == "legado@email.pt"
        assert row["estado"] == "ATIVO"
        assert versao == 1
    finally:
        caminho.unlink(missing_ok=True)
