from datetime import datetime
from typing import Optional

from src.database.database import get_connection


class ClienteResumoService:
    @staticmethod
    def _converter_datetime(valor) -> Optional[datetime]:
        if valor is None or isinstance(valor, datetime):
            return valor

        return datetime.fromisoformat(valor)

    @staticmethod
    def obter_resumo(
        cliente_id: int
    ) -> dict | None:
        """
        Obtém os principais indicadores comerciais de um cliente.
        """

        if cliente_id <= 0:
            raise ValueError(
                "O ID do cliente deve ser válido."
            )

        connection = get_connection()

        try:
            resultado = connection.execute("""
                SELECT
                    clientes.id AS cliente_id,
                    clientes.nome AS cliente_nome,

                    COUNT(pedidos.id) AS total_pedidos,

                    SUM(
                        CASE
                            WHEN pedidos.estado = 'PAGO'
                            THEN 1
                            ELSE 0
                        END
                    ) AS pedidos_pagos,

                    SUM(
                        CASE
                            WHEN pedidos.estado = 'PENDENTE'
                            THEN 1
                            ELSE 0
                        END
                    ) AS pedidos_pendentes,

                    SUM(
                        CASE
                            WHEN pedidos.estado = 'CANCELADO'
                            THEN 1
                            ELSE 0
                        END
                    ) AS pedidos_cancelados,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN pedidos.estado = 'PAGO'
                                THEN pedidos.total
                                ELSE 0
                            END
                        ),
                        0
                    ) AS faturacao_total,

                    COALESCE(
                        AVG(
                            CASE
                                WHEN pedidos.estado = 'PAGO'
                                THEN pedidos.total
                            END
                        ),
                        0
                    ) AS ticket_medio,

                    MAX(
                        CASE
                            WHEN pedidos.estado = 'PAGO'
                            THEN pedidos.pago_em
                        END
                    ) AS ultima_compra

                FROM clientes

                LEFT JOIN pedidos
                    ON pedidos.cliente_id = clientes.id

                WHERE clientes.id = ?

                GROUP BY
                    clientes.id,
                    clientes.nome
            """, (cliente_id,)).fetchone()

            if resultado is None:
                return None

            return {
                "cliente_id": resultado["cliente_id"],
                "cliente_nome": resultado["cliente_nome"],
                "total_pedidos": resultado["total_pedidos"],
                "pedidos_pagos": resultado["pedidos_pagos"],
                "pedidos_pendentes": (
                    resultado["pedidos_pendentes"]
                ),
                "pedidos_cancelados": (
                    resultado["pedidos_cancelados"]
                ),
                "faturacao_total": round(
                    float(resultado["faturacao_total"]),
                    2
                ),
                "ticket_medio": round(
                    float(resultado["ticket_medio"]),
                    2
                ),
                "ultima_compra": (
                    ClienteResumoService._converter_datetime(
                        resultado["ultima_compra"]
                    )
                )
            }

        finally:
            connection.close()
