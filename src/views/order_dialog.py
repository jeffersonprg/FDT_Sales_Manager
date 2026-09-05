"""Janelas usadas para criar e consultar pedidos na interface."""

from __future__ import annotations

import customtkinter as ctk

from src.i18n import tr
from src.models.item_pedido import ItemPedido
from src.models.pedido import Pedido
from src.presentation import (
    formatar_data,
    formatar_moeda,
    formatar_opcao_entidade,
    interpretar_decimal,
    interpretar_id_opcao,
    interpretar_inteiro_opcional,
    texto_opcional,
)
from src.views.components import DataTable
from src.views.theme import COLORS, FONT_FAMILY


class OrderDialog(ctk.CTkToplevel):
    """Monta o pedido antes de o enviar ao serviço numa única operação."""

    def __init__(self, master, clientes, produtos, on_submit):
        super().__init__(master)
        self.title(tr("Novo pedido"))
        self.geometry("860x760")
        self.minsize(760, 650)
        self.configure(fg_color=COLORS["background"])
        self.transient(master.winfo_toplevel())
        self.on_submit = on_submit
        self.itens: list[ItemPedido] = []
        self.clientes = {
            formatar_opcao_entidade(cliente.id, cliente.nome): cliente
            for cliente in clientes
        }
        self.produtos = {
            formatar_opcao_entidade(produto.id, produto.nome): produto
            for produto in produtos
        }
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_header()
        self._build_order_fields()
        self._build_items()
        self._build_footer()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Control-Return>", lambda _event: self._submit())
        self.after(50, self.grab_set)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["navy"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header, text=tr("Novo pedido"), anchor="w", text_color="white",
            font=(FONT_FAMILY, 22, "bold"),
        ).pack(fill="x", padx=26, pady=(20, 2))
        ctk.CTkLabel(
            header, text=tr("Escolha o cliente e adicione pelo menos um produto."),
            anchor="w", text_color=COLORS["header_muted"], font=(FONT_FAMILY, 11),
        ).pack(fill="x", padx=26, pady=(0, 20))

    def _build_order_fields(self):
        panel = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=12)
        panel.grid(row=1, column=0, sticky="ew", padx=22, pady=(18, 10))
        panel.grid_columnconfigure((0, 1), weight=1)
        self.cliente = self._combo_field(
            panel, 0, tr("Cliente *"), tuple(self.clientes) or (tr("— Sem clientes ativos —"),)
        )
        self.referencia = self._entry_field(panel, 1, "Referência externa")
        self.observacoes = self._entry_field(panel, 2, "Observações", columnspan=2)

    def _build_items(self):
        panel = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=12)
        panel.grid(row=2, column=0, sticky="nsew", padx=22, pady=10)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(
            panel, text=tr("Itens do pedido"), anchor="w", text_color=COLORS["text"],
            font=(FONT_FAMILY, 16, "bold"),
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        composer = ctk.CTkFrame(panel, fg_color="transparent")
        composer.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        composer.grid_columnconfigure(0, weight=1)
        self.produto = ctk.CTkComboBox(
            composer, values=list(self.produtos) or [tr("— Sem produtos ativos —")],
            height=38, state="readonly", command=self._produto_alterado,
        )
        self.produto.grid(row=0, column=0, sticky="ew")
        self.quantidade = ctk.CTkEntry(composer, width=90, height=38)
        self.quantidade.insert(0, "1")
        self.quantidade.grid(row=0, column=1, padx=(10, 0))
        self.preco = ctk.CTkEntry(composer, width=120, height=38)
        self.preco.grid(row=0, column=2, padx=(10, 0))
        ctk.CTkButton(
            composer, text=tr("Adicionar"), width=105, height=38, command=self.adicionar_item,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
        ).grid(row=0, column=3, padx=(10, 0))
        if self.produtos:
            self._produto_alterado(next(iter(self.produtos)))

        self.table = DataTable(panel, (
            ("id", "Produto ID", 85), ("produto", "Produto", 250),
            ("quantidade", "Quantidade", 95), ("preco", "Preço", 110),
            ("subtotal", "Subtotal", 120),
        ))
        self.table.grid(row=2, column=0, sticky="nsew", padx=18)
        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=18, pady=12)
        actions.grid_columnconfigure(0, weight=1)
        self.total = ctk.CTkLabel(
            actions, text=f"{tr('Total')}: € 0,00", anchor="w",
            font=(FONT_FAMILY, 16, "bold"), text_color=COLORS["text"],
        )
        self.total.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(
            actions, text=tr("Remover item"), width=120, height=34,
            command=self.remover_item, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
        ).grid(row=0, column=1)

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=22, pady=(4, 20))
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
            footer, text=tr("Criar pedido"), width=130, height=40, command=self._submit,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=(FONT_FAMILY, 12, "bold"),
        ).grid(row=1, column=2)

    def _combo_field(self, master, column, label, values):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="ew", padx=18, pady=14)
        ctk.CTkLabel(frame, text=tr(label), anchor="w").pack(fill="x")
        combo = ctk.CTkComboBox(frame, values=list(values), height=38, state="readonly")
        combo.pack(fill="x", pady=(5, 0))
        return combo

    def _entry_field(self, master, row, label, columnspan=1):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=columnspan, sticky="ew", padx=18, pady=(0, 14))
        ctk.CTkLabel(frame, text=tr(label), anchor="w").pack(fill="x")
        entry = ctk.CTkEntry(frame, height=38)
        entry.pack(fill="x", pady=(5, 0))
        return entry

    def _produto_alterado(self, opcao):
        produto = self.produtos.get(opcao)
        if produto is None:
            return
        self.preco.delete(0, "end")
        self.preco.insert(0, f"{produto.preco:.2f}".replace(".", ","))

    def adicionar_item(self):
        """Valida o item antes de o incluir no resumo visual do pedido."""

        try:
            produto_id = interpretar_id_opcao(self.produto.get())
            if produto_id is None:
                raise ValueError("Selecione um produto ativo.")
            quantidade = interpretar_inteiro_opcional(self.quantidade.get(), "quantidade")
            if quantidade is None:
                raise ValueError("A quantidade é obrigatória.")
            item = ItemPedido(
                produto_id=produto_id, quantidade=quantidade,
                preco_unitario=interpretar_decimal(self.preco.get(), "preço"),
            )
            if any(existing.produto_id == produto_id for existing in self.itens):
                raise ValueError("O produto já foi adicionado ao pedido.")
            self.itens.append(item)
            self.error.configure(text="")
            self._refresh_items()
        except Exception as error:
            self.error.configure(text=tr(str(error)))

    def remover_item(self):
        row = self.table.obter_linha_selecionada()
        if row is None:
            self.error.configure(text=tr("Selecione primeiro um item na tabela."))
            return
        produto_id = int(row[0])
        self.itens = [item for item in self.itens if item.produto_id != produto_id]
        self.error.configure(text="")
        self._refresh_items()

    def _refresh_items(self):
        nomes = {produto.id: produto.nome for produto in self.produtos.values()}
        self.table.definir_linhas([
            (item.produto_id, nomes[item.produto_id], item.quantidade,
             formatar_moeda(item.preco_unitario), formatar_moeda(item.subtotal))
            for item in self.itens
        ])
        total = sum(item.subtotal or 0 for item in self.itens)
        self.total.configure(text=f"{tr('Total')}: {formatar_moeda(total)}")

    def _submit(self):
        try:
            cliente_id = interpretar_id_opcao(self.cliente.get())
            if cliente_id is None:
                raise ValueError("Selecione um cliente ativo.")
            # O serviço grava o pedido e todos os itens na mesma transação.
            pedido = Pedido(
                cliente_id=cliente_id,
                referencia_externa=texto_opcional(self.referencia.get()),
                observacoes=texto_opcional(self.observacoes.get()),
                itens=list(self.itens),
            )
            self.on_submit(pedido)
        except Exception as error:
            self.error.configure(text=tr(str(error)))
            return
        self.destroy()


class OrderDetailsDialog(ctk.CTkToplevel):
    """Apresenta o pedido sem permitir alterações ao histórico comercial."""

    def __init__(self, master, pedido, cliente_nome, produtos):
        super().__init__(master)
        self.title(tr("Pedido #{id}", id=pedido.id))
        self.geometry("760x560")
        self.configure(fg_color=COLORS["background"])
        self.transient(master.winfo_toplevel())
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(
            self, text=tr("Pedido #{id}", id=pedido.id), anchor="w",
            font=(FONT_FAMILY, 22, "bold"), text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 4))
        resumo = tr(
            "Cliente: {customer}   ·   Estado: {status}   ·   Data: {date}   ·   Total: {total}",
            customer=cliente_nome, status=tr(pedido.estado),
            date=formatar_data(pedido.data_pedido), total=formatar_moeda(pedido.total),
        )
        ctk.CTkLabel(
            self, text=resumo, anchor="w", text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))
        table = DataTable(self, (
            ("produto", "Produto", 250), ("quantidade", "Quantidade", 100),
            ("preco", "Preço", 120), ("subtotal", "Subtotal", 120),
            ("acesso", "Acesso", 160),
        ))
        table.grid(row=2, column=0, sticky="nsew", padx=24)
        table.definir_linhas([
            (
                produtos.get(item.produto_id, tr("Produto #{id}", id=item.produto_id)),
                item.quantidade, formatar_moeda(item.preco_unitario),
                formatar_moeda(item.subtotal),
                tr("Cancelado") if pedido.estado == "CANCELADO" else (
                    tr("Aguarda pagamento") if item.inicio_acesso is None else (
                    tr("Desde {date}", date=formatar_data(item.inicio_acesso)) if item.fim_acesso is None
                    else tr("{start} a {end}", start=formatar_data(item.inicio_acesso), end=formatar_data(item.fim_acesso))
                    )
                ),
            ) for item in pedido.itens
        ])
        ctk.CTkButton(
            self, text=tr("Fechar"), width=110, command=self.destroy,
            fg_color=COLORS["navy"], hover_color=COLORS["navy_hover"],
        ).grid(row=3, column=0, sticky="e", padx=24, pady=20)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.after(50, self.grab_set)
