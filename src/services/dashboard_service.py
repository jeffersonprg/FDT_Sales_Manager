from src.database.database import get_connection


class DashboardService:
    @staticmethod
    def obter_resumo(limite_ultimos_pedidos: int = 5) -> dict:
        if limite_ultimos_pedidos <= 0:
            raise ValueError("O limite de pedidos deve ser superior a zero.")

        connection = get_connection()

        try:
            resultado = connection.execute("""
                SELECT
                    (
                        SELECT COUNT(*) FROM clientes WHERE estado = 'ATIVO'
                    ) AS total_clientes,
                    (
                        SELECT COUNT(*) FROM clientes WHERE estado = 'INATIVO'
                    ) AS total_clientes_inativos,
                    (
                        SELECT COUNT(*) FROM produtos WHERE ativo = 1
                    ) AS total_produtos_ativos,
                    (SELECT COUNT(*) FROM leads) AS total_leads,
                    (
                        SELECT COUNT(*)
                        FROM leads
                        WHERE estado IN ('NOVO', 'CONTACTADO', 'QUALIFICADO')
                    ) AS leads_abertos,
                    (
                        SELECT COUNT(*) FROM leads WHERE estado = 'CONVERTIDO'
                    ) AS leads_convertidos,
                    (SELECT COUNT(*) FROM pedidos) AS total_pedidos,
                    (
                        SELECT COUNT(*) FROM pedidos WHERE estado = 'PAGO'
                    ) AS pedidos_pagos,
                    COALESCE(
                        (
                            SELECT SUM(total)
                            FROM pedidos
                            WHERE estado = 'PAGO'
                        ),
                        0
                    ) AS faturacao_total,
                    COALESCE(
                        (
                            SELECT AVG(total)
                            FROM pedidos
                            WHERE estado = 'PAGO'
                        ),
                        0
                    ) AS ticket_medio
            """).fetchone()

            total_leads = resultado["total_leads"]
            leads_convertidos = resultado["leads_convertidos"]
            taxa_conversao = (
                0.0
                if total_leads == 0
                else round(leads_convertidos / total_leads * 100, 2)
            )

            produto_row = connection.execute("""
                SELECT
                    produtos.id AS produto_id,
                    produtos.nome AS produto_nome,
                    SUM(itens_pedido.quantidade) AS quantidade_vendida,
                    SUM(itens_pedido.subtotal) AS faturacao
                FROM itens_pedido
                INNER JOIN pedidos ON pedidos.id = itens_pedido.pedido_id
                INNER JOIN produtos ON produtos.id = itens_pedido.produto_id
                WHERE pedidos.estado = 'PAGO'
                GROUP BY produtos.id, produtos.nome
                ORDER BY quantidade_vendida DESC, faturacao DESC, produtos.nome
                LIMIT 1
            """).fetchone()

            produto_mais_vendido = None
            if produto_row is not None:
                produto_mais_vendido = {
                    "produto_id": produto_row["produto_id"],
                    "produto_nome": produto_row["produto_nome"],
                    "quantidade_vendida": produto_row["quantidade_vendida"],
                    "faturacao": round(float(produto_row["faturacao"]), 2),
                }

            rows_pedidos = connection.execute("""
                SELECT
                    pedidos.id,
                    pedidos.cliente_id,
                    clientes.nome AS cliente_nome,
                    pedidos.data_pedido,
                    pedidos.estado,
                    pedidos.total,
                    pedidos.pago_em,
                    pedidos.cancelado_em
                FROM pedidos
                INNER JOIN clientes ON clientes.id = pedidos.cliente_id
                ORDER BY pedidos.data_pedido DESC, pedidos.id DESC
                LIMIT ?
            """, (limite_ultimos_pedidos,)).fetchall()

            ultimos_pedidos = [dict(row) for row in rows_pedidos]

            return {
                "total_clientes": resultado["total_clientes"],
                "total_clientes_inativos": resultado[
                    "total_clientes_inativos"
                ],
                "total_produtos_ativos": resultado[
                    "total_produtos_ativos"
                ],
                "total_leads": total_leads,
                "leads_abertos": resultado["leads_abertos"],
                "leads_convertidos": leads_convertidos,
                "total_pedidos": resultado["total_pedidos"],
                "pedidos_pagos": resultado["pedidos_pagos"],
                "faturacao_total": round(
                    float(resultado["faturacao_total"]),
                    2,
                ),
                "ticket_medio": round(float(resultado["ticket_medio"]), 2),
                "taxa_conversao": taxa_conversao,
                "produto_mais_vendido": produto_mais_vendido,
                "ultimos_pedidos": ultimos_pedidos,
            }
        finally:
            connection.close()
