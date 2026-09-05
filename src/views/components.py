"""Componentes visuais partilhados pelas diferentes telas."""

from __future__ import annotations

import calendar
import weakref
from datetime import date
from tkinter import ttk

import customtkinter as ctk

from src.i18n import tr
from src.views.theme import COLORS, FONT_FAMILY, cor_atual


class DatePickerDialog(ctk.CTkToplevel):
    """Permite escolher uma data sem depender da digitação manual."""

    WEEKDAYS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")

    def __init__(self, master, initial_date: date | None, on_select):
        super().__init__(master)
        self.title(tr("Selecionar data"))
        self.geometry("390x430")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["background"])
        self.transient(master.winfo_toplevel())
        self.on_select = on_select
        self.selected_date = initial_date
        reference = initial_date or date.today()
        self.year = reference.year
        self.month = reference.month
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(
            header, text="‹", width=42, height=36, command=lambda: self._change_month(-1),
            fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
            hover_color=COLORS["border"], font=(FONT_FAMILY, 20, "bold"),
        ).grid(row=0, column=0)
        self.month_label = ctk.CTkLabel(
            header, text="", font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text"],
        )
        self.month_label.grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(
            header, text="›", width=42, height=36, command=lambda: self._change_month(1),
            fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
            hover_color=COLORS["border"], font=(FONT_FAMILY, 20, "bold"),
        ).grid(row=0, column=2)

        self.calendar_frame = ctk.CTkFrame(
            self, fg_color=COLORS["surface"], corner_radius=12,
            border_width=1, border_color=COLORS["border"],
        )
        self.calendar_frame.grid(row=1, column=0, sticky="ew", padx=20)
        for column in range(7):
            self.calendar_frame.grid_columnconfigure(column, weight=1)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=20, pady=18)
        actions.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(
            actions, text=tr("Limpar"), width=92, command=lambda: self._select(None),
            fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
            hover_color=COLORS["border"],
        ).grid(row=0, column=0)
        ctk.CTkButton(
            actions, text=tr("Hoje"), width=92, command=lambda: self._select(date.today()),
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
        ).grid(row=0, column=2)

        self.bind("<Escape>", lambda _event: self.destroy())
        self._render_month()
        self.after(50, self.grab_set)

    def _change_month(self, offset: int) -> None:
        """Avança ou recua o mês, incluindo a mudança automática de ano."""

        month_index = self.year * 12 + self.month - 1 + offset
        self.year, zero_based_month = divmod(month_index, 12)
        self.month = zero_based_month + 1
        self._render_month()

    def _render_month(self) -> None:
        """Reconstrói apenas a grelha dos dias do mês atualmente apresentado."""

        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        self.month_label.configure(text=f"{self.month:02d} / {self.year}")

        for column, weekday in enumerate(self.WEEKDAYS):
            ctk.CTkLabel(
                self.calendar_frame, text=tr(weekday), height=30,
                font=(FONT_FAMILY, 11, "bold"), text_color=COLORS["muted"],
            ).grid(row=0, column=column, sticky="ew", padx=2, pady=(10, 4))

        weeks = calendar.Calendar(firstweekday=calendar.MONDAY).monthdayscalendar(
            self.year, self.month
        )
        today = date.today()
        for row, week in enumerate(weeks, start=1):
            for column, day in enumerate(week):
                if day == 0:
                    continue
                current = date(self.year, self.month, day)
                selected = current == self.selected_date
                is_today = current == today
                ctk.CTkButton(
                    self.calendar_frame,
                    text=str(day),
                    width=40,
                    height=36,
                    corner_radius=18,
                    command=lambda value=current: self._select(value),
                    fg_color=COLORS["blue"] if selected else "transparent",
                    text_color="white" if selected else COLORS["text"],
                    hover_color=COLORS["blue_hover"] if selected else COLORS["surface_alt"],
                    border_width=1 if is_today and not selected else 0,
                    border_color=COLORS["blue"],
                ).grid(row=row, column=column, padx=3, pady=3)

    def _select(self, value: date | None) -> None:
        self.on_select(value)
        self.destroy()


class FormDialog(ctk.CTkToplevel):
    """Cria formulários simples a partir de uma lista de campos."""

    def __init__(
        self,
        master,
        title,
        fields,
        initial,
        on_submit,
        submit_text="Guardar",
        danger=False,
    ):
        super().__init__(master)
        self.title(tr(title))
        self.geometry("680x700")
        self.minsize(600, 560)
        self.configure(fg_color=COLORS["background"])
        self.transient(master.winfo_toplevel())
        self.on_submit = on_submit
        self.inputs = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=COLORS["navy"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header, text=tr(title), anchor="w", text_color="white",
            font=(FONT_FAMILY, 22, "bold"),
        ).pack(fill="x", padx=26, pady=22)

        form = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["surface"], corner_radius=12,
        )
        form.grid(row=1, column=0, sticky="nsew", padx=22, pady=18)
        form.grid_columnconfigure(0, weight=1)
        for row, field in enumerate(fields):
            key = field[0]
            label = field[1]
            kind = field[2] if len(field) > 2 else "entry"
            options = field[3] if len(field) > 3 else ()
            ctk.CTkLabel(
                form, text=tr(label), anchor="w", text_color=COLORS["text"],
                font=(FONT_FAMILY, 12, "bold"),
            ).grid(row=row * 2, column=0, sticky="ew", padx=16, pady=(12, 5))
            value = initial.get(key, "")
            if kind == "combo":
                widget = ctk.CTkComboBox(
                    form, values=list(options), height=38, state="readonly",
                    fg_color=COLORS["surface"], border_color=COLORS["border"],
                )
                widget.set(str(value or options[0]))
            elif kind == "text":
                widget = ctk.CTkTextbox(
                    form, height=90, fg_color=COLORS["input"],
                    border_width=1, border_color=COLORS["border"],
                )
                widget.insert("1.0", str(value or ""))
            else:
                widget = ctk.CTkEntry(
                    form, height=38, fg_color=COLORS["input"],
                    border_color=COLORS["border"],
                )
                if value not in (None, ""):
                    widget.insert(0, str(value))
            widget.grid(row=row * 2 + 1, column=0, sticky="ew", padx=16)
            self.inputs[key] = (widget, kind)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)
        self.error = ctk.CTkLabel(
            footer, text="", anchor="w", text_color=COLORS["danger"],
            font=(FONT_FAMILY, 11),
        )
        self.error.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        ctk.CTkButton(
            footer, text=tr("Cancelar"), width=110, height=40, command=self.destroy,
            fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
            hover_color=COLORS["border"],
        ).grid(row=1, column=1, padx=(0, 10))
        ctk.CTkButton(
            footer, text=tr(submit_text), width=150, height=40, command=self._submit,
            fg_color=COLORS["danger"] if danger else COLORS["blue"],
            hover_color=COLORS["danger_hover"] if danger else COLORS["blue_hover"],
            font=(FONT_FAMILY, 12, "bold"),
        ).grid(row=1, column=2)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Control-Return>", lambda _event: self._submit())
        self.after(50, self.grab_set)

    def _values(self):
        values = {}
        for key, (widget, kind) in self.inputs.items():
            values[key] = widget.get("1.0", "end").strip() if kind == "text" else widget.get()
        return values

    def _submit(self):
        # O modal permanece aberto quando o domínio rejeita algum valor.
        try:
            self.on_submit(self._values())
        except Exception as error:
            self.error.configure(text=tr(str(error)))
            return
        self.destroy()


class ConfirmationDialog(ctk.CTkToplevel):
    """Pede confirmação antes de executar uma alteração sensível."""

    def __init__(
        self,
        master,
        title,
        message,
        on_confirm,
        confirm_text="Confirmar",
        danger=False,
    ):
        super().__init__(master)
        self.title(tr(title))
        self.geometry("480x250")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["background"])
        self.transient(master.winfo_toplevel())
        self.on_confirm = on_confirm
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self, text=tr(title), anchor="w", font=(FONT_FAMILY, 20, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            self, text=tr(message), anchor="w", justify="left", wraplength=430,
            font=(FONT_FAMILY, 12), text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="ew", padx=24)
        self.error = ctk.CTkLabel(
            self, text="", anchor="w", text_color=COLORS["danger"],
            font=(FONT_FAMILY, 11),
        )
        self.error.grid(row=2, column=0, sticky="ew", padx=24, pady=(8, 0))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="e", padx=24, pady=20)
        ctk.CTkButton(
            actions, text=tr("Voltar"), width=100, command=self.destroy,
            fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
            hover_color=COLORS["border"],
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            actions, text=tr(confirm_text), width=130, command=self._confirm,
            fg_color=COLORS["danger"] if danger else COLORS["blue"],
            hover_color=COLORS["danger_hover"] if danger else COLORS["blue_hover"],
        ).pack(side="left")
        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Return>", lambda _event: self._confirm())
        self.after(50, self.grab_set)

    def _confirm(self):
        try:
            self.on_confirm()
        except Exception as error:
            self.error.configure(text=tr(str(error)))
            return
        self.destroy()


class PageHeader(ctk.CTkFrame):
    """Apresenta o título da tela e a ação opcional de atualização."""

    def __init__(self, master, title: str, subtitle: str, action=None):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self, text=tr(title), anchor="w",
            font=(FONT_FAMILY, 28, "bold"), text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            self, text=tr(subtitle), anchor="w",
            font=(FONT_FAMILY, 13), text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        if action:
            ctk.CTkButton(
                self, text=f"↻  {tr('Atualizar')}", width=116, height=38,
                command=action, fg_color=COLORS["blue"],
                hover_color=COLORS["blue_hover"],
                font=(FONT_FAMILY, 13, "bold"),
            ).grid(row=0, column=1, rowspan=2, padx=(16, 0))


class MetricCard(ctk.CTkFrame):
    """Resume um indicador do dashboard num cartão compacto."""

    def __init__(self, master, title: str, value: str, hint: str):
        super().__init__(
            master, fg_color=COLORS["surface"], corner_radius=12,
            border_width=1, border_color=COLORS["border"],
        )
        ctk.CTkLabel(
            self, text=tr(title), anchor="w", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["muted"],
        ).pack(fill="x", padx=18, pady=(16, 5))
        ctk.CTkLabel(
            self, text=value, anchor="w", font=(FONT_FAMILY, 23, "bold"),
            text_color=COLORS["text"],
        ).pack(fill="x", padx=18)
        ctk.CTkLabel(
            self, text=tr(hint), anchor="w", font=(FONT_FAMILY, 11),
            text_color=COLORS["muted"],
        ).pack(fill="x", padx=18, pady=(4, 15))


class DataTable(ctk.CTkFrame):
    """Padroniza tabelas e mantém a leitura alternada das linhas."""

    _instances = weakref.WeakSet()

    def __init__(self, master, columns: tuple[tuple[str, str, int], ...]):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=12)
        self.columns = columns
        self._instances.add(self)
        self._configurar_estilo()
        ids = tuple(column[0] for column in columns)
        self.tree = ttk.Treeview(
            self, columns=ids, show="headings", style="FDT.Treeview",
        )
        for column_id, title, width in columns:
            self.tree.heading(column_id, text=tr(title))
            self.tree.column(column_id, width=width, minwidth=70, anchor="w")
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
            style="FDT.Vertical.TScrollbar",
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)
        self.atualizar_tema()

    @staticmethod
    def _configurar_estilo() -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "FDT.Treeview", background=cor_atual("surface"),
            fieldbackground=cor_atual("surface"), foreground=cor_atual("text"),
            rowheight=36, borderwidth=0, font=(FONT_FAMILY, 10),
        )
        style.configure(
            "FDT.Treeview.Heading", background=cor_atual("surface_alt"),
            foreground=cor_atual("text"), relief="flat",
            font=(FONT_FAMILY, 10, "bold"), padding=(8, 9),
        )
        style.map(
            "FDT.Treeview",
            background=[("selected", cor_atual("selection"))],
            foreground=[("selected", cor_atual("text"))],
        )
        style.configure(
            "FDT.Vertical.TScrollbar",
            troughcolor=cor_atual("background"),
            background=cor_atual("surface_alt"),
            bordercolor=cor_atual("border"),
            arrowcolor=cor_atual("muted"),
            darkcolor=cor_atual("surface_alt"),
            lightcolor=cor_atual("surface_alt"),
        )
        style.map(
            "FDT.Vertical.TScrollbar",
            background=[("active", cor_atual("border"))],
        )

    def atualizar_tema(self) -> None:
        self._configurar_estilo()
        self.tree.tag_configure("even", background=cor_atual("surface"))
        self.tree.tag_configure("odd", background=cor_atual("table_alt"))

    @classmethod
    def atualizar_todas(cls) -> None:
        for table in tuple(cls._instances):
            if table.winfo_exists():
                table.atualizar_tema()

    def definir_linhas(self, rows):
        self.tree.delete(*self.tree.get_children())
        for index, row in enumerate(rows):
            self.tree.insert("", "end", values=row, tags=("even" if index % 2 == 0 else "odd",))
        self.atualizar_tema()

    def obter_linha_selecionada(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0], "values")


class StatusBanner(ctk.CTkLabel):
    """Mostra informação, sucesso ou erro sem interromper o utilizador."""

    def __init__(self, master):
        super().__init__(
            master, text="", anchor="w", corner_radius=8, height=36,
            font=(FONT_FAMILY, 12), fg_color=COLORS["surface_alt"],
            text_color=COLORS["muted"],
        )

    def mostrar(self, texto: str, tipo: str = "info"):
        cores = {
            "info": (COLORS["surface_alt"], COLORS["muted"]),
            "success": (COLORS["success_bg"], COLORS["success"]),
            "error": (COLORS["danger_bg"], COLORS["danger"]),
        }
        fundo, texto_cor = cores[tipo]
        self.configure(text=f"  {tr(texto)}", fg_color=fundo, text_color=texto_cor)
