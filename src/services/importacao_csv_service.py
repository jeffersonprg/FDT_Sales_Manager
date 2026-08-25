from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.database.database import create_tables, get_connection
from src.models.cliente import Cliente
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.services.pedido_service import PedidoService
from src.utils.validator import preparar_dados_csv


class ErroImportacaoCSV(ValueError):
    pass


@dataclass
class ResumoImportacaoCSV:
    arquivo: str
    hash_sha256: str
    linhas_lidas: int
    clientes_criados: int = 0
    clientes_reutilizados: int = 0
    produtos_criados: int = 0
    produtos_reutilizados: int = 0
    pedidos_criados: int = 0
    pedidos_ignorados: int = 0
    itens_criados: int = 0
    faturacao_importada: float = 0.0
    arquivo_ja_importado: bool = False
    referencias_ignoradas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class ImportacaoCSVService:
    @staticmethod
    def listar_historico(limite: int = 10) -> list[dict]:
        if limite <= 0:
            raise ValueError("O limite deve ser superior a zero.")

        create_tables()
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT *
                FROM importacoes_csv
                ORDER BY importado_em DESC, id DESC
                LIMIT ?
            """, (limite,)).fetchall()

            return [dict(row) for row in rows]
        finally:
            connection.close()

    @staticmethod
    def _calcular_hash(caminho: Path) -> str:
        digest = hashlib.sha256()

        with caminho.open("rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digest.update(bloco)

        return digest.hexdigest()

    @staticmethod
    def _ler_csv(caminho: Path) -> pd.DataFrame:
        try:
            dados = pd.read_csv(caminho, encoding="utf-8-sig")
        except (OSError, UnicodeError, pd.errors.ParserError) as error:
            raise ErroImportacaoCSV(
                f"Não foi possível ler o CSV: {error}"
            ) from error

        try:
            return preparar_dados_csv(dados)
        except ValueError as error:
            raise ErroImportacaoCSV(str(error)) from error

    @staticmethod
    def _validar_grupo_pedido(referencia: str, grupo: pd.DataFrame) -> None:
        campos_unicos = (
            "data",
            "nome_cliente",
            "morada",
            "informacao_cliente",
        )

        inconsistentes = [
            campo
            for campo in campos_unicos
            if grupo[campo].nunique(dropna=False) != 1
        ]
        if inconsistentes:
            raise ErroImportacaoCSV(
                f"O pedido {referencia} possui dados inconsistentes em: "
                + ", ".join(inconsistentes)
            )

        precos_por_produto = grupo.groupby(
            grupo["produto"].str.casefold()
        )["preco_unitario"].nunique()
        produtos_com_precos_distintos = precos_por_produto[
            precos_por_produto > 1
        ]
        if not produtos_com_precos_distintos.empty:
            raise ErroImportacaoCSV(
                f"O pedido {referencia} repete um produto com preços distintos."
            )

    @staticmethod
    def _buscar_ou_criar_cliente(
        connection: sqlite3.Connection,
        row,
        resumo: ResumoImportacaoCSV,
    ) -> int:
        rows = connection.execute("""
            SELECT id
            FROM clientes
            WHERE nome = ? COLLATE NOCASE
              AND COALESCE(morada, '') = ? COLLATE NOCASE
            ORDER BY id
        """, (row["nome_cliente"], row["morada"])).fetchall()

        if len(rows) > 1:
            raise ErroImportacaoCSV(
                "Existem vários clientes com o mesmo nome e morada: "
                f"{row['nome_cliente']}."
            )
        if rows:
            resumo.clientes_reutilizados += 1
            return rows[0]["id"]

        cliente = Cliente(
            nome=row["nome_cliente"],
            morada=row["morada"],
            observacoes=row["informacao_cliente"],
        )
        cursor = connection.execute("""
            INSERT INTO clientes (
                nome,
                morada,
                pais,
                estado,
                observacoes
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente.nome,
            cliente.morada,
            cliente.pais,
            cliente.estado,
            cliente.observacoes,
        ))
        resumo.clientes_criados += 1
        return cursor.lastrowid

    @staticmethod
    def _buscar_ou_criar_produto(
        connection: sqlite3.Connection,
        nome: str,
        preco: float,
        tipo_validade_padrao: str,
        duracao_dias_padrao: int | None,
        resumo: ResumoImportacaoCSV,
    ):
        produto_existente = connection.execute("""
            SELECT *
            FROM produtos
            WHERE nome = ? COLLATE NOCASE
        """, (nome,)).fetchone()

        if produto_existente is not None:
            resumo.produtos_reutilizados += 1
            return produto_existente

        produto = Produto(
            nome=nome,
            preco=preco,
            tipo_validade=tipo_validade_padrao,
            duracao_dias=duracao_dias_padrao,
        )
        cursor = connection.execute("""
            INSERT INTO produtos (
                nome,
                preco,
                tipo_validade,
                duracao_dias,
                ativo
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            produto.nome,
            produto.preco,
            produto.tipo_validade,
            produto.duracao_dias,
            int(produto.ativo),
        ))
        resumo.produtos_criados += 1

        return connection.execute(
            "SELECT * FROM produtos WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    @staticmethod
    def importar(
        caminho_csv: str | Path,
        tipo_validade_padrao: str = "VITALICIO",
        duracao_dias_padrao: int | None = None,
    ) -> ResumoImportacaoCSV:
        caminho = Path(caminho_csv).expanduser().resolve()
        if not caminho.is_file():
            raise ErroImportacaoCSV(f"Arquivo CSV não encontrado: {caminho}")

        produto_padrao = Produto(
            nome="Produto temporário de validação",
            preco=0,
            tipo_validade=tipo_validade_padrao,
            duracao_dias=duracao_dias_padrao,
        )
        tipo_validade_padrao = produto_padrao.tipo_validade
        duracao_dias_padrao = produto_padrao.duracao_dias

        create_tables()
        hash_arquivo = ImportacaoCSVService._calcular_hash(caminho)
        connection = get_connection()

        try:
            importacao_anterior = connection.execute("""
                SELECT total_linhas
                FROM importacoes_csv
                WHERE hash_sha256 = ?
            """, (hash_arquivo,)).fetchone()
        finally:
            connection.close()

        if importacao_anterior is not None:
            return ResumoImportacaoCSV(
                arquivo=caminho.name,
                hash_sha256=hash_arquivo,
                linhas_lidas=importacao_anterior["total_linhas"],
                arquivo_ja_importado=True,
            )

        dados = ImportacaoCSVService._ler_csv(caminho)
        resumo = ResumoImportacaoCSV(
            arquivo=caminho.name,
            hash_sha256=hash_arquivo,
            linhas_lidas=len(dados),
        )
        connection = get_connection()

        try:
            connection.execute("BEGIN IMMEDIATE")

            for referencia, grupo in dados.groupby("pedido", sort=False):
                ImportacaoCSVService._validar_grupo_pedido(referencia, grupo)

                pedido_existente = connection.execute("""
                    SELECT id
                    FROM pedidos
                    WHERE referencia_externa = ? COLLATE NOCASE
                """, (referencia,)).fetchone()
                if pedido_existente is not None:
                    resumo.pedidos_ignorados += 1
                    resumo.referencias_ignoradas.append(referencia)
                    continue

                primeira_linha = grupo.iloc[0]
                cliente_id = ImportacaoCSVService._buscar_ou_criar_cliente(
                    connection,
                    primeira_linha,
                    resumo,
                )
                data_pedido = primeira_linha["data"].to_pydatetime()
                pedido = Pedido(
                    cliente_id=cliente_id,
                    referencia_externa=referencia,
                    data_pedido=data_pedido,
                    estado="PAGO",
                    pago_em=data_pedido,
                    observacoes="Importado de arquivo CSV.",
                )

                for _, linhas_produto in grupo.groupby(
                    grupo["produto"].str.casefold(),
                    sort=False,
                ):
                    linha = linhas_produto.iloc[0]
                    quantidade = int(linhas_produto["quantidade"].sum())
                    preco_unitario = float(linha["preco_unitario"])
                    produto = ImportacaoCSVService._buscar_ou_criar_produto(
                        connection,
                        linha["produto"],
                        preco_unitario,
                        tipo_validade_padrao,
                        duracao_dias_padrao,
                        resumo,
                    )
                    item = ItemPedido(
                        produto_id=produto["id"],
                        quantidade=quantidade,
                        preco_unitario=preco_unitario,
                    )
                    PedidoService._definir_periodo_acesso(
                        item,
                        produto,
                        data_pedido,
                    )
                    pedido.adicionar_item(item)

                cursor_pedido = connection.execute("""
                    INSERT INTO pedidos (
                        cliente_id,
                        referencia_externa,
                        data_pedido,
                        estado,
                        total,
                        observacoes,
                        pago_em
                    )
                    VALUES (?, ?, ?, 'PAGO', ?, ?, ?)
                """, (
                    pedido.cliente_id,
                    pedido.referencia_externa,
                    PedidoService._serializar_datetime(pedido.data_pedido),
                    pedido.total,
                    pedido.observacoes,
                    PedidoService._serializar_datetime(pedido.pago_em),
                ))
                pedido_id = cursor_pedido.lastrowid

                for item in pedido.itens:
                    connection.execute("""
                        INSERT INTO itens_pedido (
                            pedido_id,
                            produto_id,
                            quantidade,
                            preco_unitario,
                            subtotal,
                            inicio_acesso,
                            fim_acesso
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pedido_id,
                        item.produto_id,
                        item.quantidade,
                        item.preco_unitario,
                        item.subtotal,
                        PedidoService._serializar_date(item.inicio_acesso),
                        PedidoService._serializar_date(item.fim_acesso),
                    ))
                    resumo.itens_criados += 1

                resumo.pedidos_criados += 1
                resumo.faturacao_importada = round(
                    resumo.faturacao_importada + pedido.total,
                    2,
                )

            connection.execute("""
                INSERT INTO importacoes_csv (
                    nome_arquivo,
                    hash_sha256,
                    total_linhas,
                    clientes_criados,
                    produtos_criados,
                    pedidos_criados,
                    itens_criados,
                    faturacao_importada
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resumo.arquivo,
                resumo.hash_sha256,
                resumo.linhas_lidas,
                resumo.clientes_criados,
                resumo.produtos_criados,
                resumo.pedidos_criados,
                resumo.itens_criados,
                resumo.faturacao_importada,
            ))
            connection.commit()
            return resumo

        except ErroImportacaoCSV:
            connection.rollback()
            raise
        except (ValueError, sqlite3.IntegrityError) as error:
            connection.rollback()
            raise ErroImportacaoCSV(str(error)) from error
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
