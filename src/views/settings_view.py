"""Preferências visuais da aplicação."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from src.i18n import get_language, tr
from src.views.components import PageHeader
from src.views.theme import COLORS, FONT_FAMILY


class SettingsView(ctk.CTkFrame):
    """Oferece uma alternância de tema simples e imediatamente visível."""

    def __init__(
        self,
        master,
        on_theme_change: Callable[[str], None],
        on_language_change: Callable[[str], None],
    ):
        super().__init__(master, fg_color=COLORS["background"])
        self.on_theme_change = on_theme_change
        self.on_language_change = on_language_change
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        PageHeader(
            self,
            "Configurações",
            "Personalize a experiência do FDT Sales Manager.",
        ).grid(row=0, column=0, sticky="ew", padx=28, pady=(26, 18))

        panel = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        panel.grid(row=1, column=0, sticky="ew", padx=28)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text=tr("Aparência"),
            anchor="w",
            text_color=COLORS["text"],
            font=(FONT_FAMILY, 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(20, 18))

        copy = ctk.CTkFrame(panel, fg_color="transparent")
        copy.grid(row=1, column=0, sticky="ew", padx=(22, 12), pady=(0, 22))
        ctk.CTkLabel(
            copy,
            text=tr("Tema"),
            anchor="w",
            text_color=COLORS["text"],
            font=(FONT_FAMILY, 13, "bold"),
        ).pack(fill="x")
        ctk.CTkLabel(
            copy,
            text=tr("Escolha o tema da interface. A preferência fica guardada."),
            anchor="w",
            text_color=COLORS["muted"],
            font=(FONT_FAMILY, 12),
        ).pack(fill="x", pady=(4, 0))

        controls = ctk.CTkFrame(panel, fg_color="transparent")
        controls.grid(row=1, column=1, sticky="e", padx=(12, 22), pady=(0, 22))
        ctk.CTkLabel(
            controls,
            text=tr("☀  Claro"),
            text_color=COLORS["text"],
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(side="left", padx=(0, 10))

        self.theme = ctk.StringVar(value=ctk.get_appearance_mode().casefold())
        self.switch = ctk.CTkSwitch(
            controls,
            text="",
            width=52,
            switch_width=52,
            switch_height=28,
            button_length=22,
            corner_radius=14,
            variable=self.theme,
            onvalue="dark",
            offvalue="light",
            command=self._alterar_tema,
            progress_color=COLORS["blue"],
            button_color=COLORS["surface"],
            button_hover_color=COLORS["surface_alt"],
            border_width=1,
        )
        self.switch.pack(side="left")
        ctk.CTkLabel(
            controls,
            text=tr("Escuro  ☾"),
            text_color=COLORS["text"],
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(side="left", padx=(10, 0))

        self.status = ctk.CTkLabel(
            panel,
            text="",
            anchor="w",
            text_color=COLORS["muted"],
            font=(FONT_FAMILY, 11),
        )
        self.status.grid(row=2, column=0, columnspan=2, sticky="ew", padx=22, pady=(0, 16))

        language_panel = ctk.CTkFrame(
            self, fg_color=COLORS["surface"], corner_radius=12,
            border_width=1, border_color=COLORS["border"],
        )
        language_panel.grid(row=2, column=0, sticky="ew", padx=28, pady=(14, 0))
        language_panel.grid_columnconfigure(0, weight=1)
        language_copy = ctk.CTkFrame(language_panel, fg_color="transparent")
        language_copy.grid(row=0, column=0, sticky="ew", padx=(22, 12), pady=20)
        ctk.CTkLabel(
            language_copy, text=tr("Idioma"), anchor="w",
            text_color=COLORS["text"], font=(FONT_FAMILY, 13, "bold"),
        ).pack(fill="x")
        ctk.CTkLabel(
            language_copy,
            text=tr("Escolha o idioma da interface. Os seus dados não são alterados."),
            anchor="w", text_color=COLORS["muted"], font=(FONT_FAMILY, 12),
        ).pack(fill="x", pady=(4, 0))
        self.language_names = {
            tr("Português"): "pt",
            tr("Inglês"): "en",
            tr("Espanhol"): "es",
        }
        current_name = next(
            name for name, code in self.language_names.items()
            if code == get_language()
        )
        self.language = ctk.StringVar(value=current_name)
        self.language_combo = ctk.CTkComboBox(
            language_panel, values=list(self.language_names), variable=self.language,
            state="readonly", width=180, height=38, command=self._alterar_idioma,
            fg_color=COLORS["input"], border_color=COLORS["border"],
        )
        self.language_combo.grid(row=0, column=1, sticky="e", padx=(12, 22), pady=20)

    def _alterar_tema(self) -> None:
        theme = self.theme.get()
        self.on_theme_change(theme)
        nome = tr("escuro" if theme == "dark" else "claro")
        self.status.configure(
            text=tr("Tema {name} aplicado e guardado.", name=nome),
        )

    def _alterar_idioma(self, nome: str) -> None:
        self.on_language_change(self.language_names[nome])

    def carregar(self) -> None:
        """Sincroniza o switch se o modo mudar por outra origem."""

        self.theme.set(ctk.get_appearance_mode().casefold())
