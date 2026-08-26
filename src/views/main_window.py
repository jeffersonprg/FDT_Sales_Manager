"""Janela principal e navegação entre os módulos da aplicação."""

import customtkinter as ctk

from src.presentation import NAVIGATION_ITEMS
from src.views.dashboard_view import DashboardView
from src.views.list_views import ClientesView, LeadsView, PedidosView, ProdutosView
from src.views.theme import COLORS, FONT_FAMILY
from src.views.tools_views import CSVImportView, ReportsView


class MainWindow(ctk.CTk):
    """Mantém o menu lateral e apresenta uma tela de cada vez."""

    VIEW_FACTORIES = {
        "dashboard": DashboardView,
        "clientes": ClientesView,
        "produtos": ProdutosView,
        "leads": LeadsView,
        "pedidos": PedidosView,
        "csv": CSVImportView,
        "relatorios": ReportsView,
    }

    def __init__(self):
        super().__init__()
        self.title("FDT Sales Manager")
        self.geometry("1280x800")
        self.minsize(1040, 680)
        self.configure(fg_color=COLORS["background"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.views = {}
        self.nav_buttons = {}
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        self.mostrar_view("dashboard")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=232, corner_radius=0, fg_color=COLORS["navy"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(len(NAVIGATION_ITEMS) + 2, weight=1)
        ctk.CTkLabel(
            sidebar, text="FDT", font=(FONT_FAMILY, 28, "bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(28, 0))
        ctk.CTkLabel(
            sidebar, text="Sales Manager", font=(FONT_FAMILY, 13),
            text_color="#BCCCDC", anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 24))
        for index, (key, label, icon) in enumerate(NAVIGATION_ITEMS, start=2):
            button = ctk.CTkButton(
                sidebar, text=f"{icon}   {label}", anchor="w", height=42,
                corner_radius=8, fg_color="transparent", hover_color=COLORS["navy_hover"],
                font=(FONT_FAMILY, 13, "bold"),
                command=lambda selected=key: self.mostrar_view(selected),
            )
            button.grid(row=index, column=0, sticky="ew", padx=14, pady=3)
            self.nav_buttons[key] = button
        ctk.CTkLabel(
            sidebar, text="MiniCRM · CSV · Relatórios", anchor="w",
            text_color="#829AB1", font=(FONT_FAMILY, 10),
        ).grid(row=len(NAVIGATION_ITEMS) + 3, column=0, sticky="sew", padx=24, pady=20)

    def mostrar_view(self, key):
        # As telas são criadas apenas na primeira abertura e reutilizadas depois.
        for view in self.views.values():
            view.grid_remove()
        if key not in self.views:
            self.views[key] = self.VIEW_FACTORIES[key](self.content)
            self.views[key].grid(row=0, column=0, sticky="nsew")
        else:
            self.views[key].grid()
            if hasattr(self.views[key], "carregar"):
                self.views[key].carregar()
        for nav_key, button in self.nav_buttons.items():
            button.configure(fg_color=COLORS["blue"] if nav_key == key else "transparent")
