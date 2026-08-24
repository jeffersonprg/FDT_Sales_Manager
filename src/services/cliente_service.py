import sqlite3
from datetime import datetime
from typing import Optional

from src.database.database import get_connection
from src.models.cliente import Cliente


class ClienteService:
    @staticmethod
    def _converter_datetime(valor) -> Optional[datetime]:
        if valor is None or isinstance(valor, datetime):
            return valor

        return datetime.fromisoformat(valor)

    @staticmethod
    def _row_para_cliente(row) -> Cliente:
        return Cliente(
            id=row["id"],
            nome=row["nome"],
            empresa=row["empresa"],
            morada=row["morada"],
            telefone=row["telefone"],
            email=row["email"],
            pais=row["pais"],
            tipo_documento=row["tipo_documento"],
            numero_documento=row["numero_documento"],
            estado=row["estado"],
            observacoes=row["observacoes"],
            criado_em=ClienteService._converter_datetime(row["criado_em"]),
            atualizado_em=ClienteService._converter_datetime(
                row["atualizado_em"]
            ),
        )

    @staticmethod
    def _traduzir_erro_integridade(error: sqlite3.IntegrityError) -> ValueError:
        mensagem = str(error).lower()

        if "email" in mensagem:
            return ValueError("Já existe um cliente com este email.")
        if "numero_documento" in mensagem:
            return ValueError(
                "Já existe um cliente com este número de documento."
            )

        return ValueError("Os dados do cliente violam uma regra do sistema.")

    @staticmethod
    def criar_cliente(cliente: Cliente) -> int:
        cliente_validado = Cliente(**vars(cliente))
        connection = get_connection()

        try:
            cursor = connection.execute("""
                INSERT INTO clientes (
                    nome,
                    empresa,
                    morada,
                    telefone,
                    email,
                    pais,
                    tipo_documento,
                    numero_documento,
                    estado,
                    observacoes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente_validado.nome,
                cliente_validado.empresa,
                cliente_validado.morada,
                cliente_validado.telefone,
                cliente_validado.email,
                cliente_validado.pais,
                cliente_validado.tipo_documento,
                cliente_validado.numero_documento,
                cliente_validado.estado,
                cliente_validado.observacoes,
            ))

            cliente_id = cursor.lastrowid
            if cliente_id is None:
                raise RuntimeError("Não foi possível criar o cliente.")

            connection.commit()
            cliente.__dict__.update(vars(cliente_validado))
            cliente.id = cliente_id

            return cliente_id

        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ClienteService._traduzir_erro_integridade(error) from error
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def listar_clientes(
        incluir_inativos: bool = False,
    ) -> list[Cliente]:
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT *
                FROM clientes
                WHERE ? = 1 OR estado = 'ATIVO'
                ORDER BY nome
            """, (int(incluir_inativos),)).fetchall()

            return [ClienteService._row_para_cliente(row) for row in rows]
        finally:
            connection.close()

    @staticmethod
    def buscar_cliente(
        cliente_id: int,
        incluir_inativos: bool = False,
    ) -> Cliente | None:
        if cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser válido.")

        connection = get_connection()

        try:
            row = connection.execute("""
                SELECT *
                FROM clientes
                WHERE id = ?
                  AND (? = 1 OR estado = 'ATIVO')
            """, (cliente_id, int(incluir_inativos))).fetchone()

            if row is None:
                return None

            return ClienteService._row_para_cliente(row)
        finally:
            connection.close()

    @staticmethod
    def atualizar_cliente(cliente: Cliente) -> bool:
        if cliente.id is None:
            raise ValueError(
                "O cliente deve possuir um ID para ser atualizado."
            )

        cliente_validado = Cliente(**vars(cliente))
        connection = get_connection()

        try:
            cursor = connection.execute("""
                UPDATE clientes
                SET
                    nome = ?,
                    empresa = ?,
                    morada = ?,
                    telefone = ?,
                    email = ?,
                    pais = ?,
                    tipo_documento = ?,
                    numero_documento = ?,
                    estado = ?,
                    observacoes = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                cliente_validado.nome,
                cliente_validado.empresa,
                cliente_validado.morada,
                cliente_validado.telefone,
                cliente_validado.email,
                cliente_validado.pais,
                cliente_validado.tipo_documento,
                cliente_validado.numero_documento,
                cliente_validado.estado,
                cliente_validado.observacoes,
                cliente_validado.id,
            ))

            connection.commit()
            atualizado = cursor.rowcount > 0

            if atualizado:
                cliente.__dict__.update(vars(cliente_validado))

            return atualizado

        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ClienteService._traduzir_erro_integridade(error) from error
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def remover_cliente(cliente_id: int) -> bool:
        """Desativa o cliente preservando todo o seu histórico."""

        if cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser válido.")

        connection = get_connection()

        try:
            cursor = connection.execute("""
                UPDATE clientes
                SET estado = 'INATIVO',
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ? AND estado = 'ATIVO'
            """, (cliente_id,))
            connection.commit()

            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def reativar_cliente(cliente_id: int) -> bool:
        if cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser válido.")

        connection = get_connection()

        try:
            cursor = connection.execute("""
                UPDATE clientes
                SET estado = 'ATIVO',
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ? AND estado = 'INATIVO'
            """, (cliente_id,))
            connection.commit()

            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def pesquisar_clientes(
        termo: str,
        incluir_inativos: bool = False,
    ) -> list[Cliente]:
        termo_normalizado = termo.strip()

        if not termo_normalizado:
            return ClienteService.listar_clientes(incluir_inativos)

        padrao = f"%{termo_normalizado}%"
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT *
                FROM clientes
                WHERE
                    (? = 1 OR estado = 'ATIVO')
                    AND (
                        nome COLLATE NOCASE LIKE ?
                        OR COALESCE(empresa, '') COLLATE NOCASE LIKE ?
                        OR COALESCE(email, '') COLLATE NOCASE LIKE ?
                        OR COALESCE(telefone, '') COLLATE NOCASE LIKE ?
                        OR COALESCE(pais, '') COLLATE NOCASE LIKE ?
                        OR COALESCE(numero_documento, '') COLLATE NOCASE LIKE ?
                        OR COALESCE(morada, '') COLLATE NOCASE LIKE ?
                    )
                ORDER BY nome
            """, (
                int(incluir_inativos),
                padrao,
                padrao,
                padrao,
                padrao,
                padrao,
                padrao,
                padrao,
            )).fetchall()

            return [ClienteService._row_para_cliente(row) for row in rows]
        finally:
            connection.close()
