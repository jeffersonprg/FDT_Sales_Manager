"""Janela principal e navegação entre os módulos da aplicação."""

import customtkinter as ctk
from PIL import Image, ImageTk

from src.config.paths import (
    APP_ICON_ICO_PATH,
    APP_ICON_PATH,
    BRAND_LOGO_PATH,
    BRAND_NAME,
)
from src.config.preferences import guardar_idioma, guardar_tema
from src.i18n import set_language, tr
from src.presentation import NAVIGATION_ITEMS
from src.views.components import DataTable
from src.views.dashboard_view import DashboardView
from src.views.list_views import ClientesView, LeadsView, PedidosView, ProdutosView
from src.views.settings_view import SettingsView
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
        self.title(f"{BRAND_NAME} · FDT Sales Manager")
        self.geometry("1280x800")
        self.minsize(1040, 680)
        self._aplicar_identidade_visual()
        self.configure(fg_color=COLORS["background"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.views = {}
        self.nav_buttons = {}
        self.sidebar = None
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        self.mostrar_view("dashboard")

    def _aplicar_identidade_visual(self):
        """Mantém as imagens vivas e aplica o ícone à janela no Windows."""

        with Image.open(APP_ICON_PATH) as imagem_icone:
            icone = imagem_icone.copy()
        with Image.open(BRAND_LOGO_PATH) as imagem_logo:
            logo = imagem_logo.copy()

        # Evita que o CustomTkinter restaure o seu ícone genérico após 200 ms.
        self.iconbitmap(str(APP_ICON_ICO_PATH))
        self._window_icon = ImageTk.PhotoImage(icone)
        self.iconphoto(True, self._window_icon)
        self._sidebar_logo = ctk.CTkImage(
            light_image=logo,
            dark_image=logo,
            size=(184, 144),
        )

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=232, corner_radius=0, fg_color=COLORS["navy"])
        self.sidebar = sidebar
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(len(NAVIGATION_ITEMS) + 2, weight=1)
        ctk.CTkLabel(
            sidebar, text="", image=self._sidebar_logo,
        ).grid(row=0, column=0, rowspan=2, padx=24, pady=(20, 18))
        for index, (key, label, icon) in enumerate(NAVIGATION_ITEMS, start=2):
            button = ctk.CTkButton(
                sidebar, text=f"{icon}   {tr(label)}", anchor="w", height=42,
                corner_radius=8, fg_color="transparent", hover_color=COLORS["navy_hover"],
                font=(FONT_FAMILY, 13, "bold"),
                command=lambda selected=key: self.mostrar_view(selected),
            )
            button.grid(row=index, column=0, sticky="ew", padx=14, pady=3)
            self.nav_buttons[key] = button
        ctk.CTkLabel(
            sidebar, text=tr("MiniCRM · CSV · Relatórios"), anchor="w",
            text_color=COLORS["sidebar_muted"], font=(FONT_FAMILY, 10),
        ).grid(row=len(NAVIGATION_ITEMS) + 3, column=0, sticky="sew", padx=24, pady=20)

    def mostrar_view(self, key):
        # As telas são criadas apenas na primeira abertura e reutilizadas depois.
        for view in self.views.values():
            view.grid_remove()
        if key not in self.views:
            if key == "configuracoes":
                self.views[key] = SettingsView(
                    self.content, self.alternar_tema, self.alternar_idioma,
                )
            else:
                self.views[key] = self.VIEW_FACTORIES[key](self.content)
            self.views[key].grid(row=0, column=0, sticky="nsew")
        else:
            self.views[key].grid()
            if hasattr(self.views[key], "carregar"):
                self.views[key].carregar()
        for nav_key, button in self.nav_buttons.items():
            button.configure(fg_color=COLORS["blue"] if nav_key == key else "transparent")

    def alternar_tema(self, theme: str) -> None:
        """Aplica o tema globalmente e conserva a escolha para a próxima sessão."""

        ctk.set_appearance_mode(theme)
        guardar_tema(theme)
        DataTable.atualizar_todas()

    def alternar_idioma(self, language: str) -> None:
        """Guarda o idioma e recria somente a camada visual da aplicacao."""

        set_language(language)
        guardar_idioma(language)
        for view in self.views.values():
            view.destroy()
        self.views.clear()
        self.nav_buttons.clear()
        if self.sidebar is not None:
            self.sidebar.destroy()
        self._build_sidebar()
        self.mostrar_view("configuracoes")
