from datetime import date, datetime

from src.database.database import get_connection
from src.services.pedido_service import PedidoService


class FaturacaoService:
    @staticmethod
    def _normalizar_data(valor: date | datetime | None) -> str | None:
        if valor is None:
            return None
        if isinstance(valor, datetime):
            return valor.date().isoformat()
        if isinstance(valor, date):
            return valor.isoformat()

        raise ValueError("O filtro de data deve ser válido.")

    @staticmethod
    def _normalizar_periodo(
        data_inicio: date | datetime | None,
        data_fim: date | datetime | None,
    ) -> tuple[str | None, str | None]:
        inicio = FaturacaoService._normalizar_data(data_inicio)
        fim = FaturacaoService._normalizar_data(data_fim)

        if inicio is not None and fim is not None and inicio > fim:
            raise ValueError("A data inicial não pode ser posterior à final.")

        return inicio, fim

    @staticmethod
    def obter_resumo(
        data_inicio: date | datetime | None = None,
        data_fim: date | datetime | None = None,
    ) -> dict[str, int | float]:
        inicio, fim = FaturacaoService._normalizar_periodo(
            data_inicio,
            data_fim,
        )
        connection = get_connection()

        try:
            row = connection.execute("""
                SELECT
                    COUNT(*) AS total_pedidos_pagos,
                    COALESCE(SUM(total), 0) AS faturacao_total,
                    COALESCE(AVG(total), 0) AS ticket_medio,
                    COALESCE(MIN(pago_em), NULL) AS primeiro_pagamento,
                    COALESCE(MAX(pago_em), NULL) AS ultimo_pagamento
                FROM pedidos
                WHERE estado = 'PAGO'
                  AND (? IS NULL OR DATE(pago_em) >= ?)
                  AND (? IS NULL OR DATE(pago_em) <= ?)
            """, (inicio, inicio, fim, fim)).fetchone()

            return {
                "total_pedidos_pagos": row["total_pedidos_pagos"],
                "faturacao_total": round(float(row["faturacao_total"]), 2),
                "ticket_medio": round(float(row["ticket_medio"]), 2),
                "primeiro_pagamento": row["primeiro_pagamento"],
                "ultimo_pagamento": row["ultimo_pagamento"],
            }
        finally:
            connection.close()

    @staticmethod
    def listar_pedidos_faturados(
        data_inicio: date | datetime | None = None,
        data_fim: date | datetime | None = None,
    ) -> list:
        inicio, fim = FaturacaoService._normalizar_periodo(
            data_inicio,
            data_fim,
        )
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT *
                FROM pedidos
                WHERE estado = 'PAGO'
                  AND (? IS NULL OR DATE(pago_em) >= ?)
                  AND (? IS NULL OR DATE(pago_em) <= ?)
                ORDER BY pago_em DESC, id DESC
            """, (inicio, inicio, fim, fim)).fetchall()

            return [
                PedidoService._row_para_pedido(
                    row,
                    PedidoService._listar_itens(connection, row["id"]),
                )
                for row in rows
            ]
        finally:
            connection.close()
