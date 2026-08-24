import sqlite3
from datetime import datetime, timezone
from typing import Optional

from src.database.database import get_connection
from src.models.cliente import Cliente
from src.models.lead import Lead


class LeadService:
    @staticmethod
    def _converter_datetime(valor) -> Optional[datetime]:
        if valor is None or isinstance(valor, datetime):
            return valor

        return datetime.fromisoformat(valor)

    @staticmethod
    def _row_para_lead(row) -> Lead:
        return Lead(
            id=row["id"],
            nome=row["nome"],
            empresa=row["empresa"],
            telefone=row["telefone"],
            email=row["email"],
            origem=row["origem"],
            estado=row["estado"],
            produto_interesse_id=row["produto_interesse_id"],
            cliente_id=row["cliente_id"],
            observacoes=row["observacoes"],
            convertido_em=LeadService._converter_datetime(
                row["convertido_em"]
            ),
            criado_em=LeadService._converter_datetime(
                row["criado_em"]
            ),
            atualizado_em=LeadService._converter_datetime(
                row["atualizado_em"]
            )
        )

    @staticmethod
    def _validar_produto_interesse(
        connection,
        produto_interesse_id: int | None
    ) -> None:
        if produto_interesse_id is None:
            return

        produto = connection.execute("""
            SELECT id, ativo
            FROM produtos
            WHERE id = ?
        """, (produto_interesse_id,)).fetchone()

        if produto is None:
            raise ValueError(
                "Produto de interesse não encontrado."
            )

        if not bool(produto["ativo"]):
            raise ValueError(
                "O produto de interesse está desativado."
            )

    @staticmethod
    def criar_lead(lead: Lead) -> int:
        lead_validado = Lead(**vars(lead))

        if lead_validado.estado == "CONVERTIDO":
            raise ValueError(
                "Um lead deve ser convertido através da operação "
                "de conversão para cliente."
            )

        connection = get_connection()

        try:
            LeadService._validar_produto_interesse(
                connection,
                lead_validado.produto_interesse_id
            )

            cursor = connection.execute("""
                INSERT INTO leads (
                    nome,
                    empresa,
                    telefone,
                    email,
                    origem,
                    estado,
                    produto_interesse_id,
                    observacoes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead_validado.nome,
                lead_validado.empresa,
                lead_validado.telefone,
                lead_validado.email,
                lead_validado.origem,
                lead_validado.estado,
                lead_validado.produto_interesse_id,
                lead_validado.observacoes
            ))

            connection.commit()

            lead_id = cursor.lastrowid
            lead.id = lead_id

            return lead_id

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    @staticmethod
    def buscar_lead(lead_id: int) -> Lead | None:
        connection = get_connection()

        try:
            row = connection.execute("""
                SELECT *
                FROM leads
                WHERE id = ?
            """, (lead_id,)).fetchone()

            if row is None:
                return None

            return LeadService._row_para_lead(row)

        finally:
            connection.close()

    @staticmethod
    def listar_leads(
        estado: str | None = None
    ) -> list[Lead]:
        connection = get_connection()

        try:
            if estado is None:
                rows = connection.execute("""
                    SELECT *
                    FROM leads
                    ORDER BY criado_em DESC, id DESC
                """).fetchall()

            else:
                estado_normalizado = estado.strip().upper()

                if estado_normalizado not in Lead.ESTADOS_VALIDOS:
                    raise ValueError(
                        "O estado deve ser NOVO, CONTACTADO, "
                        "QUALIFICADO, CONVERTIDO ou PERDIDO."
                    )

                rows = connection.execute("""
                    SELECT *
                    FROM leads
                    WHERE estado = ?
                    ORDER BY criado_em DESC, id DESC
                """, (estado_normalizado,)).fetchall()

            return [
                LeadService._row_para_lead(row)
                for row in rows
            ]

        finally:
            connection.close()

    @staticmethod
    def atualizar_lead(lead: Lead) -> bool:
        if lead.id is None:
            raise ValueError(
                "O lead deve possuir um ID para ser atualizado."
            )

        lead_validado = Lead(**vars(lead))

        if lead_validado.estado == "CONVERTIDO":
            raise ValueError(
                "Um lead deve ser convertido através da operação "
                "de conversão para cliente."
            )

        connection = get_connection()

        try:
            LeadService._validar_produto_interesse(
                connection,
                lead_validado.produto_interesse_id
            )

            cursor = connection.execute("""
                UPDATE leads
                SET
                    nome = ?,
                    empresa = ?,
                    telefone = ?,
                    email = ?,
                    origem = ?,
                    estado = ?,
                    produto_interesse_id = ?,
                    observacoes = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                AND estado <> 'CONVERTIDO'
            """, (
                lead_validado.nome,
                lead_validado.empresa,
                lead_validado.telefone,
                lead_validado.email,
                lead_validado.origem,
                lead_validado.estado,
                lead_validado.produto_interesse_id,
                lead_validado.observacoes,
                lead_validado.id
            ))

            connection.commit()

            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    @staticmethod
    def atualizar_estado(
        lead_id: int,
        novo_estado: str
    ) -> bool:
        estado_normalizado = novo_estado.strip().upper()

        if estado_normalizado not in Lead.ESTADOS_VALIDOS:
            raise ValueError(
                "O estado deve ser NOVO, CONTACTADO, "
                "QUALIFICADO, CONVERTIDO ou PERDIDO."
            )

        if estado_normalizado == "CONVERTIDO":
            raise ValueError(
                "Utilize a operação de conversão para transformar "
                "o lead em cliente."
            )

        connection = get_connection()

        try:
            cursor = connection.execute("""
                UPDATE leads
                SET
                    estado = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                AND estado <> 'CONVERTIDO'
            """, (
                estado_normalizado,
                lead_id
            ))

            connection.commit()

            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
            
    @staticmethod
    def converter_em_cliente(
        lead_id: int,
        morada: str | None = None,
        pais: str = "Portugal",
        tipo_documento: str | None = None,
        numero_documento: str | None = None,
        observacoes_cliente: str | None = None
    ) -> int:
        """
        Converte um lead num cliente numa única transação.
        """

        connection = get_connection()

        try:
            lead = connection.execute("""
                SELECT *
                FROM leads
                WHERE id = ?
            """, (lead_id,)).fetchone()

            if lead is None:
                raise ValueError("Lead não encontrado.")

            if lead["estado"] == "CONVERTIDO":
                raise ValueError(
                    "O lead já foi convertido em cliente."
                )

            if lead["email"] is not None:
                cliente_existente = connection.execute("""
                    SELECT id
                    FROM clientes
                    WHERE LOWER(email) = LOWER(?)
                """, (lead["email"],)).fetchone()

                if cliente_existente is not None:
                    raise ValueError(
                        "Já existe um cliente com este email."
                    )

            observacoes = observacoes_cliente
            if observacoes is None:
                observacoes = lead["observacoes"]

            cliente_validado = Cliente(
                nome=lead["nome"],
                empresa=lead["empresa"],
                morada=morada,
                telefone=lead["telefone"],
                email=lead["email"],
                pais=pais,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                observacoes=observacoes,
            )

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
                cliente_validado.observacoes
            ))

            cliente_id = cursor.lastrowid

            if cliente_id is None:
                raise RuntimeError(
                    "Não foi possível criar o cliente."
                )

            convertido_em = datetime.now(timezone.utc).replace(
                tzinfo=None
            ).isoformat(
                timespec="seconds"
            )

            cursor_atualizacao = connection.execute("""
                UPDATE leads
                SET
                    estado = 'CONVERTIDO',
                    cliente_id = ?,
                    convertido_em = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                AND estado <> 'CONVERTIDO'
            """, (
                cliente_id,
                convertido_em,
                lead_id
            ))

            if cursor_atualizacao.rowcount != 1:
                raise RuntimeError(
                    "Não foi possível atualizar o lead."
                )

            connection.commit()

            return cliente_id

        except sqlite3.IntegrityError as error:
            connection.rollback()
            mensagem = str(error).lower()

            if "email" in mensagem:
                raise ValueError(
                    "Já existe um cliente com este email."
                ) from error
            if "numero_documento" in mensagem:
                raise ValueError(
                    "Já existe um cliente com este número de documento."
                ) from error

            raise ValueError(
                "Os dados do cliente violam uma regra do sistema."
            ) from error

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
    @staticmethod
    def pesquisar_leads(
        termo: str = "",
        estado: str | None = None,
        produto_interesse_id: int | None = None
    ) -> list[Lead]:
        """
        Pesquisa leads por texto e permite filtrar por estado
        e produto de interesse.
        """

        termo_normalizado = termo.strip()
        padrao = f"%{termo_normalizado}%"

        estado_normalizado = None

        if estado is not None:
            estado_normalizado = estado.strip().upper()

            if estado_normalizado not in Lead.ESTADOS_VALIDOS:
                raise ValueError(
                    "O estado deve ser NOVO, CONTACTADO, "
                    "QUALIFICADO, CONVERTIDO ou PERDIDO."
                )

        if (
            produto_interesse_id is not None
            and produto_interesse_id <= 0
        ):
            raise ValueError(
                "O ID do produto de interesse deve ser válido."
            )

        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT leads.*
                FROM leads

                LEFT JOIN produtos
                    ON produtos.id = leads.produto_interesse_id

                WHERE
                    (
                        ? = ''
                        OR leads.nome COLLATE NOCASE LIKE ?
                        OR COALESCE(leads.empresa, '')
                            COLLATE NOCASE LIKE ?
                        OR COALESCE(leads.telefone, '')
                            COLLATE NOCASE LIKE ?
                        OR COALESCE(leads.email, '')
                            COLLATE NOCASE LIKE ?
                        OR COALESCE(leads.origem, '')
                            COLLATE NOCASE LIKE ?
                        OR COALESCE(leads.observacoes, '')
                            COLLATE NOCASE LIKE ?
                        OR COALESCE(produtos.nome, '')
                            COLLATE NOCASE LIKE ?
                    )

                    AND (
                        ? IS NULL
                        OR leads.estado = ?
                    )

                    AND (
                        ? IS NULL
                        OR leads.produto_interesse_id = ?
                    )

                ORDER BY
                    leads.criado_em DESC,
                    leads.id DESC
            """, (
                termo_normalizado,
                padrao,
                padrao,
                padrao,
                padrao,
                padrao,
                padrao,
                padrao,
                estado_normalizado,
                estado_normalizado,
                produto_interesse_id,
                produto_interesse_id
            )).fetchall()

            return [
                LeadService._row_para_lead(row)
                for row in rows
            ]

        finally:
            connection.close()
