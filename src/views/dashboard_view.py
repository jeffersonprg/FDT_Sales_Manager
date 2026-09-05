"""Dashboard híbrido ligado aos indicadores reais do MiniCRM."""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from src.i18n import tr
from src.presentation import formatar_moeda, montar_dashboard
from src.services.dashboard_service import DashboardService
from src.services.estatisticas_service import EstatisticasService
from src.views.components import DataTable, MetricCard, PageHeader
from src.views.theme import COLORS, FONT_FAMILY, cor_atual


class DashboardChart(ctk.CTkFrame):
    """Painel leve que desenha gráficos sem depender do Matplotlib."""

    def __init__(self, master, title: str, subtitle: str, chart_type: str):
        super().__init__(
            master, fg_color=COLORS["surface"], corner_radius=12,
            border_width=1, border_color=COLORS["border"],
        )
        self.chart_type = chart_type
        self.data: list[tuple[str, float]] = []
        self._redraw_job = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self, text=tr(title), anchor="w",
            font=(FONT_FAMILY, 16, "bold"), text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 2))
        ctk.CTkLabel(
            self, text=tr(subtitle), anchor="w",
            font=(FONT_FAMILY, 10), text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="ew", padx=18)

        self.canvas = tk.Canvas(
            self, height=220, highlightthickness=0,
            background=cor_atual("surface"),
        )
        self.canvas.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 12))
        self.canvas.bind("<Configure>", self._agendar_redesenho)

    def definir_dados(self, data: list[tuple[str, float]]) -> None:
        self.data = data
        self._agendar_redesenho()

    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        if hasattr(self, "canvas"):
            self.canvas.configure(background=cor_atual("surface", mode_string))
            self._agendar_redesenho()

    def _agendar_redesenho(self, _event=None) -> None:
        if not hasattr(self, "canvas"):
            return
        if self._redraw_job is not None:
            self.after_cancel(self._redraw_job)
        self._redraw_job = self.after(30, self._desenhar)

    def _desenhar(self) -> None:
        self._redraw_job = None
        self.canvas.delete("all")
        largura = max(self.canvas.winfo_width(), 320)
        altura = max(self.canvas.winfo_height(), 190)
        if not self.data:
            self.canvas.create_text(
                largura / 2, altura / 2,
                text=tr("Ainda não existem vendas pagas para apresentar."),
                fill=cor_atual("muted"), font=(FONT_FAMILY, 10),
                width=max(largura - 50, 200), justify="center",
            )
            return
        if self.chart_type == "bars":
            self._desenhar_barras(largura, altura)
        else:
            self._desenhar_linha(largura, altura)

    def _desenhar_barras(self, largura: int, altura: int) -> None:
        margem_nome = min(max(largura * 0.31, 105), 150)
        margem_direita = 18
        area = max(largura - margem_nome - margem_direita, 80)
        espacamento = max((altura - 14) / len(self.data), 30)
        altura_barra = min(20, espacamento * 0.48)
        maior = max(valor for _, valor in self.data) or 1

        for indice, (nome, valor) in enumerate(self.data):
            centro_y = 8 + espacamento * (indice + 0.5)
            topo = centro_y - altura_barra / 2
            nome_curto = nome if len(nome) <= 20 else nome[:19] + "…"
            self.canvas.create_text(
                margem_nome - 10, centro_y, text=nome_curto, anchor="e",
                fill=cor_atual("text"), font=(FONT_FAMILY, 9),
            )
            self.canvas.create_rectangle(
                margem_nome, topo, margem_nome + area, topo + altura_barra,
                fill=cor_atual("surface_alt"), outline="",
            )
            largura_barra = max(area * valor / maior, 2)
            self.canvas.create_rectangle(
                margem_nome, topo, margem_nome + largura_barra,
                topo + altura_barra, fill=cor_atual("blue"), outline="",
            )
            ancora = "e" if largura_barra > 105 else "w"
            x = (
                margem_nome + largura_barra - 6
                if ancora == "e" else margem_nome + largura_barra + 6
            )
            self.canvas.create_text(
                x, centro_y, text=formatar_moeda(valor), anchor=ancora,
                fill="white" if ancora == "e" else cor_atual("muted"),
                font=(FONT_FAMILY, 8, "bold"),
            )

    def _desenhar_linha(self, largura: int, altura: int) -> None:
        esquerda, direita, topo, base = 54, 14, 14, 34
        area_x = max(largura - esquerda - direita, 100)
        area_y = max(altura - topo - base, 80)
        maior = max(valor for _, valor in self.data) or 1

        for fracao in (0, 0.5, 1):
            y = topo + area_y * (1 - fracao)
            self.canvas.create_line(
                esquerda, y, esquerda + area_x, y,
                fill=cor_atual("border"),
            )
            self.canvas.create_text(
                esquerda - 7, y, text=self._moeda_compacta(maior * fracao),
                anchor="e", fill=cor_atual("muted"),
                font=(FONT_FAMILY, 8),
            )

        divisor = max(len(self.data) - 1, 1)
        pontos = []
        for indice, (mes, valor) in enumerate(self.data):
            x = esquerda + area_x * indice / divisor
            if len(self.data) == 1:
                x = esquerda + area_x / 2
            y = topo + area_y * (1 - valor / maior)
            pontos.append((x, y, mes, valor))

        if len(pontos) > 1:
            coordenadas = [coordenada for ponto in pontos for coordenada in ponto[:2]]
            self.canvas.create_line(
                *coordenadas, fill=cor_atual("success"), width=3,
                smooth=True, splinesteps=18,
            )

        passo_rotulo = max((len(pontos) + 5) // 6, 1)
        for indice, (x, y, mes, _valor) in enumerate(pontos):
            self.canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill=cor_atual("success"), outline=cor_atual("surface"), width=2,
            )
            if indice % passo_rotulo == 0 or indice == len(pontos) - 1:
                self.canvas.create_text(
                    x, topo + area_y + 18, text=self._formatar_mes(mes),
                    anchor="n", fill=cor_atual("muted"),
                    font=(FONT_FAMILY, 8),
                )

    @staticmethod
    def _formatar_mes(valor: str) -> str:
        partes = valor.split("-", 1)
        return f"{partes[1]}/{partes[0]}" if len(partes) == 2 else valor

    @staticmethod
    def _moeda_compacta(valor: float) -> str:
        if abs(valor) >= 1_000_000:
            return f"€ {valor / 1_000_000:.1f}M".replace(".", ",")
        if abs(valor) >= 1_000:
            return f"€ {valor / 1_000:.1f}k".replace(".", ",")
        return f"€ {valor:.0f}"


class DashboardView(ctk.CTkFrame):
    """Organiza indicadores, gráficos, destaques e pedidos recentes."""

    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        PageHeader(
            self, "Dashboard", "Visão geral do desempenho comercial.", self.carregar,
        ).grid(row=0, column=0, sticky="ew", padx=28, pady=(26, 12))

        self.body = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
        )
        self.body.grid(row=1, column=0, sticky="nsew", padx=(20, 12), pady=(0, 14))
        self.body.grid_columnconfigure(0, weight=1)

        self.cards_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.cards_frame.grid(row=0, column=0, sticky="ew", padx=8)
        for column in range(3):
            self.cards_frame.grid_columnconfigure(column, weight=1, uniform="cards")

        self.charts = ctk.CTkFrame(self.body, fg_color="transparent")
        self.charts.grid(row=1, column=0, sticky="ew", padx=8, pady=(8, 0))
        self.charts.grid_columnconfigure((0, 1), weight=1, uniform="charts")
        self.grafico_mensal = DashboardChart(
            self.charts, "Evolução mensal da faturação",
            "Últimos 12 meses com vendas pagas", "line",
        )
        self.grafico_mensal.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.grafico_produtos = DashboardChart(
            self.charts, "Faturação por produto",
            "Até 5 produtos com maior faturação", "bars",
        )
        self.grafico_produtos.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.insights = ctk.CTkFrame(
            self.body, fg_color=COLORS["surface"], corner_radius=12,
            border_width=1, border_color=COLORS["border"],
        )
        self.insights.grid(row=2, column=0, sticky="ew", padx=8, pady=14)
        self.insights.grid_columnconfigure((0, 1), weight=1)
        self.conversao = self._insight(0, tr("Taxa de conversão"))
        self.produto = self._insight(1, tr("Produto em destaque"))

        ctk.CTkLabel(
            self.body, text=tr("Pedidos recentes"), anchor="w",
            font=(FONT_FAMILY, 17, "bold"), text_color=COLORS["text"],
        ).grid(row=3, column=0, sticky="ew", padx=10, pady=(2, 8))
        self.table = DataTable(self.body, (
            ("id", "Pedido", 90), ("cliente", "Cliente", 230),
            ("data", "Data", 120), ("estado", "Estado", 110),
            ("total", "Total", 120),
        ))
        self.table.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 12))
        self.table.configure(height=225)
        self.table.grid_propagate(False)
        self.carregar()

    def _insight(self, column, title):
        frame = ctk.CTkFrame(self.insights, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="ew", padx=20, pady=16)
        ctk.CTkLabel(
            frame, text=title, anchor="w", font=(FONT_FAMILY, 11, "bold"),
            text_color=COLORS["muted"],
        ).pack(fill="x")
        label = ctk.CTkLabel(
            frame, text="—", anchor="w", font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"],
        )
        label.pack(fill="x", pady=(5, 0))
        return label

    def carregar(self):
        # A apresentação transforma os dados; esta tela apenas os distribui.
        dados = montar_dashboard(DashboardService.obter_resumo())
        produtos = sorted(
            EstatisticasService.vendas_por_produto(),
            key=lambda item: item["faturacao_total"], reverse=True,
        )[:5]
        meses = EstatisticasService.faturacao_por_mes()[-12:]

        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for index, card in enumerate(dados["cards"]):
            MetricCard(self.cards_frame, *card).grid(
                row=index // 3, column=index % 3, sticky="ew",
                padx=(0 if index % 3 == 0 else 8, 0), pady=(0, 8),
            )
        self.grafico_produtos.definir_dados([
            (item["produto_nome"], float(item["faturacao_total"]))
            for item in produtos
        ])
        self.grafico_mensal.definir_dados([
            (item["mes"], float(item["faturacao_total"]))
            for item in meses
        ])
        self.conversao.configure(text=dados["taxa_conversao"])
        self.produto.configure(text=dados["produto_destaque"])
        self.table.definir_linhas(dados["pedidos"])
