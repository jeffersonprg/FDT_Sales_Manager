"""Componentes visuais partilhados pelas diferentes telas."""

from __future__ import annotations

from tkinter import ttk

import customtkinter as ctk

from src.views.theme import COLORS, FONT_FAMILY


class FormDialog(ctk.CTkToplevel):
    """Cria formulários simples a partir de uma lista de campos."""

    def __init__(self, master, title, fields, initial, on_submit):
        super().__init__(master)
        self.title(title)
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
            header, text=title, anchor="w", text_color="white",
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
                form, text=label, anchor="w", text_color=COLORS["text"],
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
                    form, height=90, fg_color="#F8FAFC",
                    border_width=1, border_color=COLORS["border"],
                )
                widget.insert("1.0", str(value or ""))
            else:
                widget = ctk.CTkEntry(
                    form, height=38, fg_color="#F8FAFC",
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
            footer, text="Cancelar", width=110, height=40, command=self.destroy,
            fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
            hover_color=COLORS["border"],
        ).grid(row=1, column=1, padx=(0, 10))
        ctk.CTkButton(
            footer, text="Guardar", width=130, height=40, command=self._submit,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=(FONT_FAMILY, 12, "bold"),
        ).grid(row=1, column=2)
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
            self.error.configure(text=str(error))
            return
        self.destroy()


class PageHeader(ctk.CTkFrame):
    """Apresenta o título da tela e a ação opcional de atualização."""

    def __init__(self, master, title: str, subtitle: str, action=None):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self, text=title, anchor="w",
            font=(FONT_FAMILY, 28, "bold"), text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            self, text=subtitle, anchor="w",
            font=(FONT_FAMILY, 13), text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        if action:
            ctk.CTkButton(
                self, text="↻  Atualizar", width=116, height=38,
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
            self, text=title, anchor="w", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["muted"],
        ).pack(fill="x", padx=18, pady=(16, 5))
        ctk.CTkLabel(
            self, text=value, anchor="w", font=(FONT_FAMILY, 23, "bold"),
            text_color=COLORS["text"],
        ).pack(fill="x", padx=18)
        ctk.CTkLabel(
            self, text=hint, anchor="w", font=(FONT_FAMILY, 11),
            text_color=COLORS["muted"],
        ).pack(fill="x", padx=18, pady=(4, 15))


class DataTable(ctk.CTkFrame):
    """Padroniza tabelas e mantém a leitura alternada das linhas."""

    def __init__(self, master, columns: tuple[tuple[str, str, int], ...]):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=12)
        self.columns = columns
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "FDT.Treeview", background=COLORS["surface"],
            fieldbackground=COLORS["surface"], foreground=COLORS["text"],
            rowheight=36, borderwidth=0, font=(FONT_FAMILY, 10),
        )
        style.configure(
            "FDT.Treeview.Heading", background=COLORS["surface_alt"],
            foreground=COLORS["text"], relief="flat",
            font=(FONT_FAMILY, 10, "bold"), padding=(8, 9),
        )
        style.map("FDT.Treeview", background=[("selected", "#DBEAFE")],
                  foreground=[("selected", COLORS["text"])])
        ids = tuple(column[0] for column in columns)
        self.tree = ttk.Treeview(
            self, columns=ids, show="headings", style="FDT.Treeview",
        )
        for column_id, title, width in columns:
            self.tree.heading(column_id, text=title)
            self.tree.column(column_id, width=width, minwidth=70, anchor="w")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

    def definir_linhas(self, rows):
        self.tree.delete(*self.tree.get_children())
        for index, row in enumerate(rows):
            self.tree.insert("", "end", values=row, tags=("even" if index % 2 == 0 else "odd",))
        self.tree.tag_configure("even", background=COLORS["surface"])
        self.tree.tag_configure("odd", background="#F8FAFC")

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
            "success": ("#E6FFFA", COLORS["success"]),
            "error": ("#FFF5F5", COLORS["danger"]),
        }
        fundo, texto_cor = cores[tipo]
        self.configure(text=f"  {texto}", fg_color=fundo, text_color=texto_cor)
