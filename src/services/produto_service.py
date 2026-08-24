import sqlite3

from src.database.database import get_connection
from src.models.produto import Produto


class ProdutoService:
    @staticmethod
    def _row_para_produto(row) -> Produto:
        return Produto(
            id=row["id"],
            nome=row["nome"],
            categoria=row["categoria"],
            preco=row["preco"],
            descricao=row["descricao"],
            tipo_validade=row["tipo_validade"],
            duracao_dias=row["duracao_dias"],
            ativo=bool(row["ativo"]),
        )

    @staticmethod
    def _traduzir_erro_integridade(error: sqlite3.IntegrityError) -> ValueError:
        if "nome" in str(error).lower():
            return ValueError("Já existe um produto com este nome.")

        return ValueError("Os dados do produto violam uma regra do sistema.")

    @staticmethod
    def criar_produto(produto: Produto) -> int:
        produto_validado = Produto(**vars(produto))
        connection = get_connection()

        try:
            cursor = connection.execute("""
                INSERT INTO produtos (
                    nome,
                    categoria,
                    preco,
                    descricao,
                    tipo_validade,
                    duracao_dias,
                    ativo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                produto_validado.nome,
                produto_validado.categoria,
                produto_validado.preco,
                produto_validado.descricao,
                produto_validado.tipo_validade,
                produto_validado.duracao_dias,
                int(produto_validado.ativo),
            ))

            produto_id = cursor.lastrowid
            if produto_id is None:
                raise RuntimeError("Não foi possível criar o produto.")

            connection.commit()
            produto.__dict__.update(vars(produto_validado))
            produto.id = produto_id

            return produto_id

        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ProdutoService._traduzir_erro_integridade(error) from error
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def listar_produtos(apenas_ativos: bool = False) -> list[Produto]:
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT *
                FROM produtos
                WHERE ? = 0 OR ativo = 1
                ORDER BY nome
            """, (int(apenas_ativos),)).fetchall()

            return [ProdutoService._row_para_produto(row) for row in rows]
        finally:
            connection.close()

    @staticmethod
    def buscar_produto(produto_id: int) -> Produto | None:
        if produto_id <= 0:
            raise ValueError("O ID do produto deve ser válido.")

        connection = get_connection()

        try:
            row = connection.execute(
                "SELECT * FROM produtos WHERE id = ?",
                (produto_id,),
            ).fetchone()

            if row is None:
                return None

            return ProdutoService._row_para_produto(row)
        finally:
            connection.close()

    @staticmethod
    def atualizar_produto(produto: Produto) -> bool:
        if produto.id is None:
            raise ValueError(
                "O produto deve possuir um ID para ser atualizado."
            )

        produto_validado = Produto(**vars(produto))
        connection = get_connection()

        try:
            cursor = connection.execute("""
                UPDATE produtos
                SET
                    nome = ?,
                    categoria = ?,
                    preco = ?,
                    descricao = ?,
                    tipo_validade = ?,
                    duracao_dias = ?,
                    ativo = ?
                WHERE id = ?
            """, (
                produto_validado.nome,
                produto_validado.categoria,
                produto_validado.preco,
                produto_validado.descricao,
                produto_validado.tipo_validade,
                produto_validado.duracao_dias,
                int(produto_validado.ativo),
                produto_validado.id,
            ))

            connection.commit()
            atualizado = cursor.rowcount > 0

            if atualizado:
                produto.__dict__.update(vars(produto_validado))

            return atualizado

        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ProdutoService._traduzir_erro_integridade(error) from error
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def desativar_produto(produto_id: int) -> bool:
        return ProdutoService._alterar_atividade(produto_id, ativo=False)

    @staticmethod
    def reativar_produto(produto_id: int) -> bool:
        return ProdutoService._alterar_atividade(produto_id, ativo=True)

    @staticmethod
    def _alterar_atividade(produto_id: int, ativo: bool) -> bool:
        if produto_id <= 0:
            raise ValueError("O ID do produto deve ser válido.")

        connection = get_connection()

        try:
            cursor = connection.execute("""
                UPDATE produtos
                SET ativo = ?
                WHERE id = ? AND ativo <> ?
            """, (int(ativo), produto_id, int(ativo)))
            connection.commit()

            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def pesquisar_produtos(
        termo: str,
        apenas_ativos: bool = False,
    ) -> list[Produto]:
        termo_normalizado = termo.strip()
        padrao = f"%{termo_normalizado}%"
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT *
                FROM produtos
                WHERE
                    (
                        ? = ''
                        OR nome COLLATE NOCASE LIKE ?
                        OR COALESCE(categoria, '') COLLATE NOCASE LIKE ?
                        OR COALESCE(descricao, '') COLLATE NOCASE LIKE ?
                        OR tipo_validade COLLATE NOCASE LIKE ?
                    )
                    AND (? = 0 OR ativo = 1)
                ORDER BY nome
            """, (
                termo_normalizado,
                padrao,
                padrao,
                padrao,
                padrao,
                int(apenas_ativos),
            )).fetchall()

            return [ProdutoService._row_para_produto(row) for row in rows]
        finally:
            connection.close()
