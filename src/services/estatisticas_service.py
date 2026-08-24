from datetime import date, datetime

from src.database.database import get_connection
from src.services.faturacao_service import FaturacaoService


class EstatisticasService:
    @staticmethod
    def obter_resumo_vendas(
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
                    COUNT(DISTINCT pedidos.id) AS total_pedidos,
                    COALESCE(SUM(itens_pedido.quantidade), 0)
                        AS quantidade_vendida,
                    COALESCE(SUM(itens_pedido.subtotal), 0)
                        AS faturacao_total
                FROM pedidos
                LEFT JOIN itens_pedido
                    ON itens_pedido.pedido_id = pedidos.id
                WHERE pedidos.estado = 'PAGO'
                  AND (? IS NULL OR DATE(pedidos.pago_em) >= ?)
                  AND (? IS NULL OR DATE(pedidos.pago_em) <= ?)
            """, (inicio, inicio, fim, fim)).fetchone()

            total_pedidos = row["total_pedidos"]
            faturacao_total = round(float(row["faturacao_total"]), 2)

            return {
                "total_pedidos": total_pedidos,
                "quantidade_vendida": row["quantidade_vendida"],
                "faturacao_total": faturacao_total,
                "media_por_pedido": (
                    0.0
                    if total_pedidos == 0
                    else round(faturacao_total / total_pedidos, 2)
                ),
            }
        finally:
            connection.close()

    @staticmethod
    def vendas_por_produto(
        data_inicio: date | datetime | None = None,
        data_fim: date | datetime | None = None,
    ) -> list[dict]:
        inicio, fim = FaturacaoService._normalizar_periodo(
            data_inicio,
            data_fim,
        )
        connection = get_connection()

        try:
            rows = connection.execute("""
                SELECT
                    produtos.id AS produto_id,
                    produtos.nome AS produto_nome,
                    produtos.categoria,
                    SUM(itens_pedido.quantidade) AS quantidade_vendida,
                    SUM(itens_pedido.subtotal) AS faturacao_total,
                    AVG(itens_pedido.preco_unitario) AS preco_medio
                FROM itens_pedido
                INNER JOIN pedidos ON pedidos.id = itens_pedido.pedido_id
                INNER JOIN produtos ON produtos.id = itens_pedido.produto_id
                WHERE pedidos.estado = 'PAGO'
                  AND (? IS NULL OR DATE(pedidos.pago_em) >= ?)
                  AND (? IS NULL OR DATE(pedidos.pago_em) <= ?)
                GROUP BY produtos.id, produtos.nome, produtos.categoria
                ORDER BY quantidade_vendida DESC, faturacao_total DESC,
                         produtos.nome
            """, (inicio, inicio, fim, fim)).fetchall()

            return [
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "categoria": row["categoria"],
                    "quantidade_vendida": row["quantidade_vendida"],
                    "faturacao_total": round(
                        float(row["faturacao_total"]),
                        2,
                    ),
                    "preco_medio": round(float(row["preco_medio"]), 2),
                }
                for row in rows
            ]
        finally:
            connection.close()
