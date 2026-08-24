from datetime import date, datetime
from typing import Optional

from src.database.database import get_connection


class AcessoService:
    @staticmethod
    def _converter_date(valor) -> Optional[date]:
        if valor is None or isinstance(valor, date):
            return valor

        return date.fromisoformat(valor)

    @staticmethod
    def _converter_datetime(valor) -> Optional[datetime]:
        if valor is None or isinstance(valor, datetime):
            return valor

        return datetime.fromisoformat(valor)

    @staticmethod
    def listar_acessos_cliente(
        cliente_id: int,
        apenas_ativos: bool = False,
        data_referencia: date | None = None
    ) -> list[dict]:
        """
        Lista os acessos concedidos por pedidos pagos.
        """

        if cliente_id <= 0:
            raise ValueError(
                "O ID do cliente deve ser válido."
            )

        data_referencia = data_referencia or date.today()

        connection = get_connection()

        try:
            cliente = connection.execute("""
                SELECT id
                FROM clientes
                WHERE id = ?
            """, (cliente_id,)).fetchone()

            if cliente is None:
                raise ValueError("Cliente não encontrado.")

            rows = connection.execute("""
                SELECT
                    itens_pedido.id AS item_pedido_id,
                    pedidos.id AS pedido_id,
                    pedidos.data_pedido,
                    pedidos.pago_em,
                    produtos.id AS produto_id,
                    produtos.nome AS produto_nome,
                    produtos.categoria,
                    produtos.tipo_validade,
                    itens_pedido.quantidade,
                    itens_pedido.preco_unitario,
                    itens_pedido.subtotal,
                    itens_pedido.inicio_acesso,
                    itens_pedido.fim_acesso

                FROM itens_pedido

                INNER JOIN pedidos
                    ON pedidos.id = itens_pedido.pedido_id

                INNER JOIN produtos
                    ON produtos.id = itens_pedido.produto_id

                WHERE pedidos.cliente_id = ?
                  AND pedidos.estado = 'PAGO'

                ORDER BY
                    itens_pedido.inicio_acesso DESC,
                    itens_pedido.id DESC
            """, (cliente_id,)).fetchall()

            acessos = []

            for row in rows:
                inicio_acesso = AcessoService._converter_date(
                    row["inicio_acesso"]
                )

                fim_acesso = AcessoService._converter_date(
                    row["fim_acesso"]
                )

                ativo = (
                    inicio_acesso is not None
                    and inicio_acesso <= data_referencia
                    and (
                        fim_acesso is None
                        or data_referencia <= fim_acesso
                    )
                )

                if apenas_ativos and not ativo:
                    continue

                acessos.append({
                    "item_pedido_id": row["item_pedido_id"],
                    "pedido_id": row["pedido_id"],
                    "data_pedido": (
                        AcessoService._converter_datetime(
                            row["data_pedido"]
                        )
                    ),
                    "pago_em": (
                        AcessoService._converter_datetime(
                            row["pago_em"]
                        )
                    ),
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "categoria": row["categoria"],
                    "tipo_validade": row["tipo_validade"],
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                    "subtotal": row["subtotal"],
                    "inicio_acesso": inicio_acesso,
                    "fim_acesso": fim_acesso,
                    "ativo": ativo
                })

            return acessos

        finally:
            connection.close()
