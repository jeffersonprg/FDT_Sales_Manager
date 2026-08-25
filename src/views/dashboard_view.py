import customtkinter as ctk

from src.presentation import montar_dashboard
from src.services.dashboard_service import DashboardService
from src.views.components import DataTable, MetricCard, PageHeader
from src.views.theme import COLORS, FONT_FAMILY


class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        PageHeader(
            self, "Dashboard", "Visão geral do desempenho comercial.", self.carregar,
        ).grid(row=0, column=0, sticky="ew", padx=28, pady=(26, 18))
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", padx=28)
        for column in range(3):
            self.cards_frame.grid_columnconfigure(column, weight=1)
        self.insights = ctk.CTkFrame(
            self, fg_color=COLORS["surface"], corner_radius=12,
            border_width=1, border_color=COLORS["border"],
        )
        self.insights.grid(row=2, column=0, sticky="ew", padx=28, pady=16)
        self.insights.grid_columnconfigure((0, 1), weight=1)
        self.conversao = self._insight(0, "Taxa de conversão")
        self.produto = self._insight(1, "Produto em destaque")
        self.table = DataTable(self, (
            ("id", "Pedido", 90), ("cliente", "Cliente", 230),
            ("data", "Data", 120), ("estado", "Estado", 110),
            ("total", "Total", 120),
        ))
        self.table.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 26))
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
        dados = montar_dashboard(DashboardService.obter_resumo())
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for index, card in enumerate(dados["cards"]):
            MetricCard(self.cards_frame, *card).grid(
                row=index // 3, column=index % 3, sticky="ew",
                padx=(0 if index % 3 == 0 else 8, 0), pady=(0, 8),
            )
        self.conversao.configure(text=dados["taxa_conversao"])
        self.produto.configure(text=dados["produto_destaque"])
        self.table.definir_linhas(dados["pedidos"])
