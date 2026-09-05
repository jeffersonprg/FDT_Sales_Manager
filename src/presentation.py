"""Formatação e conversão de dados usados pela interface gráfica."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from src.i18n import tr


NAVIGATION_ITEMS = (
    ("dashboard", "Dashboard", "▦"),
    ("clientes", "Clientes", "◉"),
    ("produtos", "Produtos", "◆"),
    ("leads", "Leads", "◎"),
    ("pedidos", "Pedidos", "▤"),
    ("csv", "Importar CSV", "⇧"),
    ("relatorios", "Relatórios", "▥"),
    ("configuracoes", "Configurações", "⚙"),
)


def formatar_moeda(valor: Any) -> str:
    numero = float(valor or 0)
    formatado = f"{numero:,.2f}"
    return "€ " + formatado.replace(",", "X").replace(".", ",").replace(
        "X", "."
    )


def formatar_data(valor: Any, incluir_hora: bool = False) -> str:
    if valor in (None, ""):
        return "—"
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor)
    if isinstance(valor, date) and not isinstance(valor, datetime):
        valor = datetime.combine(valor, datetime.min.time())
    formato = "%d/%m/%Y %H:%M" if incluir_hora else "%d/%m/%Y"
    return valor.strftime(formato)


def formatar_texto(valor: Any) -> str:
    return "—" if valor in (None, "") else str(valor)


def interpretar_data_filtro(valor: str) -> date | None:
    """Lê a data amigável da interface e mantém compatibilidade com o formato antigo."""

    texto = valor.strip()
    if not texto:
        return None
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    raise ValueError("Use datas no formato DD/MM/AAAA.")


def interpretar_datetime_evento(valor: str) -> datetime | None:
    """Converte a data informada na interface ou deixa o serviço usar o momento atual."""

    texto = valor.strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M")
    except ValueError as error:
        raise ValueError("Use data e hora no formato AAAA-MM-DD HH:MM.") from error


def interpretar_decimal(valor: str, campo: str = "valor") -> float:
    texto = valor.strip().replace("€", "").replace(" ", "")
    if not texto:
        raise ValueError(f"O {campo} é obrigatório.")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return round(float(texto), 2)
    except ValueError as error:
        raise ValueError(f"O {campo} deve ser numérico.") from error


def interpretar_inteiro_opcional(valor: str, campo: str) -> int | None:
    texto = valor.strip()
    if not texto:
        return None
    try:
        numero = int(texto)
    except ValueError as error:
        raise ValueError(f"O {campo} deve ser um número inteiro.") from error
    return numero


def texto_opcional(valor: str) -> str | None:
    texto = valor.strip()
    return texto or None


def formatar_opcao_entidade(entidade_id: int, nome: str) -> str:
    return f"{entidade_id} · {nome}"


def interpretar_id_opcao(valor: str) -> int | None:
    texto = valor.strip()
    if not texto or texto.startswith("—"):
        return None
    try:
        return int(texto.split("·", 1)[0].strip())
    except (ValueError, IndexError) as error:
        raise ValueError("A opção selecionada não é válida.") from error


def montar_dashboard(resumo: dict) -> dict:
    """Prepara indicadores e linhas sem criar dependência com o Tk."""

    produto = resumo.get("produto_mais_vendido")
    cards = (
        (tr("Clientes ativos"), str(resumo.get("total_clientes", 0)), tr("base atual")),
        (tr("Produtos ativos"), str(resumo.get("total_produtos_ativos", 0)), tr("catálogo")),
        (tr("Leads abertos"), str(resumo.get("leads_abertos", 0)), tr("em acompanhamento")),
        (tr("Pedidos pagos"), str(resumo.get("pedidos_pagos", 0)), tr("concluídos")),
        (tr("Faturação"), formatar_moeda(resumo.get("faturacao_total")), tr("total pago")),
        (tr("Ticket médio"), formatar_moeda(resumo.get("ticket_medio")), tr("por pedido pago")),
    )
    pedidos = []
    for pedido in resumo.get("ultimos_pedidos", []):
        pedidos.append((
            f"#{pedido['id']}",
            pedido.get("cliente_nome", "—"),
            formatar_data(pedido.get("data_pedido")),
            pedido.get("estado", "—"),
            formatar_moeda(pedido.get("total")),
        ))
    return {
        "cards": cards,
        "taxa_conversao": f"{float(resumo.get('taxa_conversao', 0)):.1f}%",
        "produto_destaque": tr("Nenhuma venda registada") if produto is None else (
            tr("{product} · {quantity} vendidos", product=produto['produto_nome'],
               quantity=produto['quantidade_vendida'])
        ),
        "pedidos": pedidos,
    }
