import sqlite3
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from src.database.database import get_connection
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido


class PedidoService:
    TRANSICOES_VALIDAS = {
        "PENDENTE": {"PAGO", "CANCELADO"},
        "PAGO": {"CANCELADO"},
        "CANCELADO": set(),
    }

    @staticmethod
    def _agora_utc() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _converter_datetime(valor) -> Optional[datetime]:
        if valor is None or isinstance(valor, datetime):
            return valor

        return datetime.fromisoformat(valor)

    @staticmethod
    def _converter_date(valor) -> Optional[date]:
        if valor is None or isinstance(valor, date):
            return valor

        return date.fromisoformat(valor)

    @staticmethod
    def _serializar_datetime(valor: Optional[datetime]) -> Optional[str]:
        return None if valor is None else valor.isoformat(timespec="seconds")

    @staticmethod
    def _serializar_date(valor: Optional[date]) -> Optional[str]:
        return None if valor is None else valor.isoformat()

    @staticmethod
    def _row_para_item(row) -> ItemPedido:
        return ItemPedido(
            id=row["id"],
            pedido_id=row["pedido_id"],
            produto_id=row["produto_id"],
            quantidade=row["quantidade"],
            preco_unitario=row["preco_unitario"],
            subtotal=row["subtotal"],
            inicio_acesso=PedidoService._converter_date(
                row["inicio_acesso"]
            ),
            fim_acesso=PedidoService._converter_date(row["fim_acesso"]),
        )

    @staticmethod
    def _row_para_pedido(row, itens: list[ItemPedido]) -> Pedido:
        return Pedido(
            id=row["id"],
            cliente_id=row["cliente_id"],
            referencia_externa=row["referencia_externa"],
            data_pedido=PedidoService._converter_datetime(row["data_pedido"]),
            estado=row["estado"],
            total=row["total"],
            observacoes=row["observacoes"],
            pago_em=PedidoService._converter_datetime(row["pago_em"]),
            cancelado_em=PedidoService._converter_datetime(
                row["cancelado_em"]
            ),
            criado_em=PedidoService._converter_datetime(row["criado_em"]),
            atualizado_em=PedidoService._converter_datetime(
                row["atualizado_em"]
            ),
            itens=itens,
        )

    @staticmethod
    def _definir_periodo_acesso(
        item: ItemPedido,
        produto,
        data_pagamento: datetime,
    ) -> None:
        inicio_esperado = data_pagamento.date()

        if (
            item.inicio_acesso is not None
            and item.inicio_acesso != inicio_esperado
        ):
            raise ValueError(
                f"A data de início do produto {item.produto_id} "
                "deve corresponder à data de pagamento."
            )

        if produto["tipo_validade"] == "VITALICIO":
            if item.fim_acesso is not None:
                raise ValueError(
                    f"O produto {item.produto_id} é vitalício "
                    "e não deve possuir data de fim."
                )

            item.inicio_acesso = inicio_esperado
            item.fim_acesso = None
            return

        fim_esperado = inicio_esperado + timedelta(
            days=produto["duracao_dias"] - 1
        )

        if item.fim_acesso is not None and item.fim_acesso != fim_esperado:
            raise ValueError(
                f"A data de fim do produto {item.produto_id} "
                "não corresponde à duração cadastrada."
            )

        item.inicio_acesso = inicio_esperado
        item.fim_acesso = fim_esperado

    @staticmethod
    def _listar_itens(
        connection: sqlite3.Connection,
        pedido_id: int,
    ) -> list[ItemPedido]:
        rows = connection.execute("""
            SELECT *
            FROM itens_pedido
            WHERE pedido_id = ?
            ORDER BY id
        """, (pedido_id,)).fetchall()

        return [PedidoService._row_para_item(row) for row in rows]

    @staticmethod
    def _buscar_produto_ativo(
        connection: sqlite3.Connection,
        produto_id: int,
    ):
        produto = connection.execute("""
            SELECT id, ativo, tipo_validade, duracao_dias
            FROM produtos
            WHERE id = ?
        """, (produto_id,)).fetchone()

        if produto is None:
            raise ValueError(f"Produto {produto_id} não encontrado.")
        if not bool(produto["ativo"]):
            raise ValueError(f"O produto {produto_id} está desativado.")

        return produto

    @staticmethod
    def _traduzir_erro_integridade(error: sqlite3.IntegrityError) -> ValueError:
        if "referencia_externa" in str(error).lower():
            return ValueError("Já existe um pedido com esta referência externa.")

        return ValueError("Os dados do pedido violam uma regra do sistema.")

    @staticmethod
    def criar_pedido(pedido: Pedido) -> int:
        if not pedido.itens:
            raise ValueError("O pedido deve possuir pelo menos um item.")

        pedido_validado = Pedido(
            id=pedido.id,
            cliente_id=pedido.cliente_id,
            referencia_externa=pedido.referencia_externa,
            data_pedido=pedido.data_pedido,
            estado=pedido.estado,
            total=pedido.total,
            observacoes=pedido.observacoes,
            pago_em=pedido.pago_em,
            cancelado_em=pedido.cancelado_em,
            criado_em=pedido.criado_em,
            atualizado_em=pedido.atualizado_em,
            itens=[ItemPedido(**vars(item)) for item in pedido.itens],
        )

        produtos_ids = [item.produto_id for item in pedido_validado.itens]
        if len(produtos_ids) != len(set(produtos_ids)):
            raise ValueError("O produto já foi adicionado ao pedido.")

        if pedido_validado.estado != "PAGO" and any(
            item.inicio_acesso is not None or item.fim_acesso is not None
            for item in pedido_validado.itens
        ):
            raise ValueError(
                "Pedidos não pagos não podem possuir período de acesso."
            )

        pedido_validado.total = pedido_validado.calcular_total()
        connection = get_connection()

        try:
            cliente = connection.execute("""
                SELECT id, estado
                FROM clientes
                WHERE id = ?
            """, (pedido_validado.cliente_id,)).fetchone()

            if cliente is None:
                raise ValueError("Cliente não encontrado.")
            if cliente["estado"] != "ATIVO":
                raise ValueError("Não é possível criar pedido para cliente inativo.")

            for item in pedido_validado.itens:
                produto = PedidoService._buscar_produto_ativo(
                    connection,
                    item.produto_id,
                )

                if pedido_validado.estado == "PAGO":
                    PedidoService._definir_periodo_acesso(
                        item,
                        produto,
                        pedido_validado.pago_em,
                    )

            cursor = connection.execute("""
                INSERT INTO pedidos (
                    cliente_id,
                    referencia_externa,
                    data_pedido,
                    estado,
                    total,
                    observacoes,
                    pago_em,
                    cancelado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pedido_validado.cliente_id,
                pedido_validado.referencia_externa,
                PedidoService._serializar_datetime(
                    pedido_validado.data_pedido
                ),
                pedido_validado.estado,
                pedido_validado.total,
                pedido_validado.observacoes,
                PedidoService._serializar_datetime(pedido_validado.pago_em),
                PedidoService._serializar_datetime(
                    pedido_validado.cancelado_em
                ),
            ))

            pedido_id = cursor.lastrowid
            if pedido_id is None:
                raise RuntimeError("Não foi possível criar o pedido.")

            for item in pedido_validado.itens:
                item_cursor = connection.execute("""
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
                item.id = item_cursor.lastrowid
                item.pedido_id = pedido_id

            connection.commit()
            pedido.__dict__.update(vars(pedido_validado))
            pedido.id = pedido_id

            for original, validado in zip(
                pedido.itens,
                pedido_validado.itens,
                strict=True,
            ):
                original.__dict__.update(vars(validado))

            return pedido_id

        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise PedidoService._traduzir_erro_integridade(error) from error
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def buscar_pedido(pedido_id: int) -> Pedido | None:
        if pedido_id <= 0:
            raise ValueError("O ID do pedido deve ser válido.")

        connection = get_connection()

        try:
            row_pedido = connection.execute(
                "SELECT * FROM pedidos WHERE id = ?",
                (pedido_id,),
            ).fetchone()

            if row_pedido is None:
                return None

            itens = PedidoService._listar_itens(connection, pedido_id)
            return PedidoService._row_para_pedido(row_pedido, itens)
        finally:
            connection.close()

    @staticmethod
    def listar_pedidos(cliente_id: int | None = None) -> list[Pedido]:
        if cliente_id is not None and cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser válido.")

        connection = get_connection()

        try:
            if cliente_id is None:
                rows_pedidos = connection.execute("""
                    SELECT *
                    FROM pedidos
                    ORDER BY data_pedido DESC, id DESC
                """).fetchall()
            else:
                rows_pedidos = connection.execute("""
                    SELECT *
                    FROM pedidos
                    WHERE cliente_id = ?
                    ORDER BY data_pedido DESC, id DESC
                """, (cliente_id,)).fetchall()

            return [
                PedidoService._row_para_pedido(
                    row,
                    PedidoService._listar_itens(connection, row["id"]),
                )
                for row in rows_pedidos
            ]
        finally:
            connection.close()

    @staticmethod
    def atualizar_estado_pedido(
        pedido_id: int,
        novo_estado: str,
        data_evento: datetime | None = None,
    ) -> bool:
        if pedido_id <= 0:
            raise ValueError("O ID do pedido deve ser válido.")

        estado_normalizado = novo_estado.strip().upper()
        if estado_normalizado not in Pedido.ESTADOS_VALIDOS:
            raise ValueError("O estado deve ser PENDENTE, PAGO ou CANCELADO.")
        if data_evento is not None and not isinstance(data_evento, datetime):
            raise ValueError("A data do evento deve ser válida.")

        connection = get_connection()

        try:
            pedido = connection.execute(
                "SELECT * FROM pedidos WHERE id = ?",
                (pedido_id,),
            ).fetchone()

            if pedido is None:
                return False

            estado_atual = pedido["estado"]
            if estado_normalizado == estado_atual:
                return True
            if estado_normalizado not in PedidoService.TRANSICOES_VALIDAS[
                estado_atual
            ]:
                raise ValueError(
                    f"Não é permitido alterar um pedido {estado_atual} "
                    f"para {estado_normalizado}."
                )

            momento_evento = data_evento or PedidoService._agora_utc()
            data_pedido = PedidoService._converter_datetime(
                pedido["data_pedido"]
            )
            if momento_evento < data_pedido:
                raise ValueError(
                    "A data do evento não pode ser anterior à data do pedido."
                )

            if estado_normalizado == "PAGO":
                rows_itens = connection.execute("""
                    SELECT
                        itens_pedido.*,
                        produtos.ativo,
                        produtos.tipo_validade,
                        produtos.duracao_dias
                    FROM itens_pedido
                    INNER JOIN produtos
                        ON produtos.id = itens_pedido.produto_id
                    WHERE itens_pedido.pedido_id = ?
                    ORDER BY itens_pedido.id
                """, (pedido_id,)).fetchall()

                for row in rows_itens:
                    item = PedidoService._row_para_item(row)
                    item.inicio_acesso = None
                    item.fim_acesso = None
                    PedidoService._definir_periodo_acesso(
                        item,
                        row,
                        momento_evento,
                    )
                    connection.execute("""
                        UPDATE itens_pedido
                        SET inicio_acesso = ?, fim_acesso = ?
                        WHERE id = ?
                    """, (
                        PedidoService._serializar_date(item.inicio_acesso),
                        PedidoService._serializar_date(item.fim_acesso),
                        item.id,
                    ))

                connection.execute("""
                    UPDATE pedidos
                    SET estado = 'PAGO',
                        pago_em = ?,
                        cancelado_em = NULL,
                        atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    PedidoService._serializar_datetime(momento_evento),
                    pedido_id,
                ))
            else:
                pago_em = PedidoService._converter_datetime(pedido["pago_em"])
                if pago_em is not None and momento_evento < pago_em:
                    raise ValueError(
                        "O cancelamento não pode ser anterior ao pagamento."
                    )

                connection.execute("""
                    UPDATE pedidos
                    SET estado = 'CANCELADO',
                        cancelado_em = ?,
                        atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    PedidoService._serializar_datetime(momento_evento),
                    pedido_id,
                ))

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def buscar_por_referencia_externa(
        referencia_externa: str,
    ) -> Pedido | None:
        referencia = referencia_externa.strip()
        if not referencia:
            raise ValueError("A referência externa não pode estar vazia.")

        connection = get_connection()

        try:
            row_pedido = connection.execute("""
                SELECT *
                FROM pedidos
                WHERE referencia_externa = ? COLLATE NOCASE
            """, (referencia,)).fetchone()

            if row_pedido is None:
                return None

            itens = PedidoService._listar_itens(
                connection,
                row_pedido["id"],
            )
            return PedidoService._row_para_pedido(row_pedido, itens)
        finally:
            connection.close()
