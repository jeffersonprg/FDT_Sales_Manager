import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "src" / "data"
DATABASE_PATH = DATA_DIR / "fdt_sales_manager.db"


def get_connection() -> sqlite3.Connection:
    """Cria uma conexão SQLite configurada para o MiniCRM."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")

    return connection


def _coluna_existe(
    connection: sqlite3.Connection,
    tabela: str,
    coluna: str,
) -> bool:
    colunas = connection.execute(
        f"PRAGMA table_info({tabela})"
    ).fetchall()

    return any(item["name"] == coluna for item in colunas)


def _migracao_aplicada(
    connection: sqlite3.Connection,
    versao: int,
) -> bool:
    row = connection.execute(
        "SELECT 1 FROM schema_migrations WHERE versao = ?",
        (versao,),
    ).fetchone()

    return row is not None


def _garantir_sem_duplicados(
    connection: sqlite3.Connection,
    tabela: str,
    coluna: str,
    descricao: str,
) -> None:
    duplicados = connection.execute(f"""
        SELECT LOWER(TRIM({coluna})) AS valor, COUNT(*) AS total
        FROM {tabela}
        WHERE {coluna} IS NOT NULL
          AND TRIM({coluna}) <> ''
        GROUP BY LOWER(TRIM({coluna}))
        HAVING COUNT(*) > 1
    """).fetchall()

    if duplicados:
        valores = ", ".join(row["valor"] for row in duplicados)
        raise RuntimeError(
            f"Não foi possível aplicar a unicidade de {descricao}. "
            f"Valores duplicados: {valores}."
        )


def _migrar_schema(connection: sqlite3.Connection) -> None:
    """Aplica migrações incrementais sem apagar dados existentes."""

    connection.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            versao INTEGER PRIMARY KEY,
            aplicado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    if _migracao_aplicada(connection, 1):
        return

    if not _coluna_existe(connection, "clientes", "estado"):
        connection.execute("""
            ALTER TABLE clientes
            ADD COLUMN estado TEXT NOT NULL DEFAULT 'ATIVO'
        """)

    if not _coluna_existe(
        connection,
        "pedidos",
        "referencia_externa",
    ):
        connection.execute("""
            ALTER TABLE pedidos
            ADD COLUMN referencia_externa TEXT
        """)

    if not _coluna_existe(connection, "pedidos", "pago_em"):
        connection.execute("""
            ALTER TABLE pedidos
            ADD COLUMN pago_em TIMESTAMP
        """)

    if not _coluna_existe(connection, "pedidos", "cancelado_em"):
        connection.execute("""
            ALTER TABLE pedidos
            ADD COLUMN cancelado_em TIMESTAMP
        """)

    _garantir_sem_duplicados(
        connection,
        "clientes",
        "email",
        "email de cliente",
    )
    _garantir_sem_duplicados(
        connection,
        "clientes",
        "numero_documento",
        "número de documento",
    )
    _garantir_sem_duplicados(
        connection,
        "produtos",
        "nome",
        "nome de produto",
    )
    _garantir_sem_duplicados(
        connection,
        "pedidos",
        "referencia_externa",
        "referência externa de pedido",
    )

    connection.execute("""
        UPDATE clientes
        SET email = LOWER(TRIM(email))
        WHERE email IS NOT NULL AND TRIM(email) <> ''
    """)
    connection.execute("""
        UPDATE clientes
        SET email = NULL
        WHERE email IS NOT NULL AND TRIM(email) = ''
    """)
    connection.execute("""
        UPDATE clientes
        SET numero_documento = TRIM(numero_documento)
        WHERE numero_documento IS NOT NULL
    """)
    connection.execute("""
        UPDATE produtos
        SET nome = TRIM(nome)
    """)
    connection.execute("""
        UPDATE pedidos
        SET referencia_externa = TRIM(referencia_externa)
        WHERE referencia_externa IS NOT NULL
    """)

    connection.execute("""
        UPDATE pedidos
        SET pago_em = data_pedido
        WHERE estado = 'PAGO' AND pago_em IS NULL
    """)
    connection.execute("""
        UPDATE pedidos
        SET cancelado_em = COALESCE(atualizado_em, data_pedido)
        WHERE estado = 'CANCELADO' AND cancelado_em IS NULL
    """)
    connection.execute("""
        UPDATE itens_pedido
        SET inicio_acesso = NULL,
            fim_acesso = NULL
        WHERE pedido_id IN (
            SELECT id FROM pedidos WHERE estado <> 'PAGO'
        )
    """)
    connection.execute("""
        UPDATE itens_pedido
        SET fim_acesso = DATE(fim_acesso, '-1 day')
        WHERE fim_acesso IS NOT NULL
          AND pedido_id IN (
              SELECT pedidos.id
              FROM pedidos
              WHERE pedidos.estado = 'PAGO'
          )
          AND produto_id IN (
              SELECT produtos.id
              FROM produtos
              WHERE produtos.tipo_validade = 'TEMPORARIO'
          )
    """)

    connection.execute("DROP INDEX IF EXISTS idx_pedidos_referencia_externa")
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
            idx_clientes_email_nocase
        ON clientes(email COLLATE NOCASE)
        WHERE email IS NOT NULL AND TRIM(email) <> ''
    """)
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
            idx_clientes_numero_documento_nocase
        ON clientes(numero_documento COLLATE NOCASE)
        WHERE numero_documento IS NOT NULL
          AND TRIM(numero_documento) <> ''
    """)
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
            idx_produtos_nome_nocase
        ON produtos(nome COLLATE NOCASE)
    """)
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
            idx_pedidos_referencia_externa
        ON pedidos(referencia_externa COLLATE NOCASE)
        WHERE referencia_externa IS NOT NULL
          AND TRIM(referencia_externa) <> ''
    """)
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_pedidos_pago_em
        ON pedidos(pago_em)
    """)

    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_clientes_estado_insert
        BEFORE INSERT ON clientes
        WHEN NEW.estado NOT IN ('ATIVO', 'INATIVO')
        BEGIN
            SELECT RAISE(ABORT, 'estado de cliente inválido');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_clientes_estado_update
        BEFORE UPDATE OF estado ON clientes
        WHEN NEW.estado NOT IN ('ATIVO', 'INATIVO')
        BEGIN
            SELECT RAISE(ABORT, 'estado de cliente inválido');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_pedidos_pago_em_insert
        BEFORE INSERT ON pedidos
        WHEN NEW.estado = 'PAGO' AND NEW.pago_em IS NULL
        BEGIN
            SELECT RAISE(ABORT, 'pedido pago exige data de pagamento');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_pedidos_pago_em_update
        BEFORE UPDATE OF estado, pago_em ON pedidos
        WHEN NEW.estado = 'PAGO' AND NEW.pago_em IS NULL
        BEGIN
            SELECT RAISE(ABORT, 'pedido pago exige data de pagamento');
        END
    """)

    connection.execute(
        "INSERT INTO schema_migrations (versao) VALUES (1)"
    )


def create_tables() -> None:
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL CHECK (LENGTH(TRIM(nome)) > 0),
                empresa TEXT,
                morada TEXT,
                telefone TEXT,
                email TEXT UNIQUE,
                pais TEXT NOT NULL DEFAULT 'Portugal',
                tipo_documento TEXT,
                numero_documento TEXT,
                estado TEXT NOT NULL DEFAULT 'ATIVO'
                    CHECK (estado IN ('ATIVO', 'INATIVO')),
                observacoes TEXT,
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
                    CHECK (LENGTH(TRIM(nome)) > 0),
                categoria TEXT,
                preco REAL NOT NULL CHECK (preco >= 0),
                descricao TEXT,
                tipo_validade TEXT NOT NULL
                    CHECK (tipo_validade IN ('TEMPORARIO', 'VITALICIO')),
                duracao_dias INTEGER,
                ativo INTEGER NOT NULL DEFAULT 1
                    CHECK (ativo IN (0, 1)),
                CHECK (
                    (tipo_validade = 'VITALICIO' AND duracao_dias IS NULL)
                    OR
                    (
                        tipo_validade = 'TEMPORARIO'
                        AND duracao_dias IS NOT NULL
                        AND duracao_dias > 0
                    )
                )
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                referencia_externa TEXT,
                data_pedido TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                estado TEXT NOT NULL DEFAULT 'PENDENTE'
                    CHECK (estado IN ('PENDENTE', 'PAGO', 'CANCELADO')),
                total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
                observacoes TEXT,
                pago_em TIMESTAMP,
                cancelado_em TIMESTAMP,
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                CHECK (estado <> 'PAGO' OR pago_em IS NOT NULL)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 1
                    CHECK (quantidade > 0),
                preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
                subtotal REAL NOT NULL CHECK (subtotal >= 0),
                inicio_acesso DATE,
                fim_acesso DATE,
                FOREIGN KEY (pedido_id)
                    REFERENCES pedidos(id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE,
                FOREIGN KEY (produto_id)
                    REFERENCES produtos(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                UNIQUE (pedido_id, produto_id),
                CHECK (fim_acesso IS NULL OR inicio_acesso IS NOT NULL),
                CHECK (fim_acesso IS NULL OR fim_acesso >= inicio_acesso)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL CHECK (LENGTH(TRIM(nome)) > 0),
                empresa TEXT,
                telefone TEXT,
                email TEXT,
                origem TEXT,
                estado TEXT NOT NULL DEFAULT 'NOVO'
                    CHECK (
                        estado IN (
                            'NOVO',
                            'CONTACTADO',
                            'QUALIFICADO',
                            'CONVERTIDO',
                            'PERDIDO'
                        )
                    ),
                produto_interesse_id INTEGER,
                cliente_id INTEGER,
                observacoes TEXT,
                convertido_em TIMESTAMP,
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_interesse_id)
                    REFERENCES produtos(id)
                    ON UPDATE CASCADE
                    ON DELETE SET NULL,
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                CHECK (
                    (
                        estado = 'CONVERTIDO'
                        AND cliente_id IS NOT NULL
                        AND convertido_em IS NOT NULL
                    )
                    OR
                    (
                        estado <> 'CONVERTIDO'
                        AND cliente_id IS NULL
                        AND convertido_em IS NULL
                    )
                )
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_leads_estado
            ON leads(estado)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_leads_produto_interesse
            ON leads(produto_interesse_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_leads_cliente
            ON leads(cliente_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_pedidos_cliente
            ON pedidos(cliente_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_pedidos_estado
            ON pedidos(estado)
        """)
        _migrar_schema(connection)
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def verificar_tabelas() -> list[str]:
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """).fetchall()

        return [row["name"] for row in rows]

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()
    print("Tabelas disponíveis:")
    for nome_tabela in verificar_tabelas():
        print(nome_tabela)
