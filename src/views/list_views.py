from __future__ import annotations

import customtkinter as ctk

from src.models.cliente import Cliente
from src.models.lead import Lead
from src.models.produto import Produto
from src.presentation import (
    formatar_data,
    formatar_moeda,
    formatar_texto,
    interpretar_decimal,
    interpretar_id_opcao,
    interpretar_inteiro_opcional,
    formatar_opcao_entidade,
    texto_opcional,
)
from src.services.cliente_service import ClienteService
from src.services.lead_service import LeadService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService
from src.views.components import DataTable, FormDialog, PageHeader, StatusBanner
from src.views.theme import COLORS, FONT_FAMILY


class ListView(ctk.CTkFrame):
    def __init__(self, master, title, subtitle, columns):
        super().__init__(master, fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        PageHeader(self, title, subtitle, self.carregar).grid(
            row=0, column=0, sticky="ew", padx=28, pady=(26, 18)
        )
        self.filters = ctk.CTkFrame(self, fg_color="transparent")
        self.filters.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))
        self.filters.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(
            self.filters, placeholder_text="Pesquisar…", height=38,
            fg_color=COLORS["surface"], border_color=COLORS["border"],
            font=(FONT_FAMILY, 12),
        )
        self.search.grid(row=0, column=0, sticky="ew")
        self.search.bind("<Return>", lambda _event: self.carregar())
        ctk.CTkButton(
            self.filters, text="Pesquisar", width=100, height=38, command=self.carregar,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
        ).grid(row=0, column=1, padx=(10, 0))
        self.table = DataTable(self, columns)
        self.table.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 10))
        self.status = StatusBanner(self)
        self.status.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 26))
        self.status.mostrar("Selecione uma linha para editar ou alterar o estado.")

    def carregar(self):
        self.table.definir_linhas(self.obter_linhas(self.search.get().strip()))

    def adicionar_acao(self, texto, command, destaque=False):
        column = max(
            int(widget.grid_info()["column"])
            for widget in self.filters.grid_slaves(row=0)
        ) + 1
        button = ctk.CTkButton(
            self.filters, text=texto, width=110, height=38, command=command,
            fg_color=COLORS["blue"] if destaque else COLORS["navy"],
            hover_color=COLORS["blue_hover"] if destaque else COLORS["navy_hover"],
            font=(FONT_FAMILY, 11, "bold"),
        )
        button.grid(row=0, column=column, padx=(10, 0))
        return button

    def id_selecionado(self):
        row = self.table.obter_linha_selecionada()
        if row is None:
            self.status.mostrar("Selecione primeiro um registo na tabela.", "error")
            return None
        return int(row[0])


class ClientesView(ListView):
    def __init__(self, master):
        super().__init__(master, "Clientes", "Clientes ativos e respetivos contactos.", (
            ("id", "ID", 60), ("nome", "Nome", 210), ("empresa", "Empresa", 170),
            ("email", "Email", 220), ("telefone", "Telefone", 130),
            ("pais", "País", 100), ("estado", "Estado", 90),
        ))
        self.adicionar_acao("Novo cliente", self.novo, destaque=True)
        self.adicionar_acao("Editar", self.editar)
        self.adicionar_acao("Ativar/Inativar", self.alternar_estado)
        self.table.tree.bind("<Double-1>", lambda _event: self.editar())
        self.carregar()

    FIELDS = (
        ("nome", "Nome *"), ("empresa", "Empresa"), ("email", "Email"),
        ("telefone", "Telefone"), ("morada", "Morada"), ("pais", "País"),
        ("tipo_documento", "Tipo de documento"),
        ("numero_documento", "Número do documento"),
        ("observacoes", "Observações", "text"),
    )

    def obter_linhas(self, termo):
        clientes = ClienteService.pesquisar_clientes(termo, incluir_inativos=True)
        return [(c.id, c.nome, formatar_texto(c.empresa), formatar_texto(c.email),
                 formatar_texto(c.telefone), c.pais, c.estado) for c in clientes]

    def novo(self):
        self.dialog = FormDialog(
            self, "Novo cliente", self.FIELDS, {"pais": "Portugal"}, self._criar,
        )

    def _cliente_dos_valores(self, values, cliente_id=None, estado="ATIVO"):
        return Cliente(
            id=cliente_id, nome=values["nome"], empresa=texto_opcional(values["empresa"]),
            email=texto_opcional(values["email"]), telefone=texto_opcional(values["telefone"]),
            morada=texto_opcional(values["morada"]), pais=values["pais"],
            tipo_documento=texto_opcional(values["tipo_documento"]),
            numero_documento=texto_opcional(values["numero_documento"]),
            observacoes=texto_opcional(values["observacoes"]), estado=estado,
        )

    def _criar(self, values):
        ClienteService.criar_cliente(self._cliente_dos_valores(values))
        self.carregar()
        self.status.mostrar("Cliente criado com sucesso.", "success")

    def editar(self):
        cliente_id = self.id_selecionado()
        if cliente_id is None:
            return
        cliente = ClienteService.buscar_cliente(cliente_id, incluir_inativos=True)
        initial = {key: getattr(cliente, key) or "" for key, *_ in self.FIELDS}
        self.dialog = FormDialog(
            self, "Editar cliente", self.FIELDS, initial,
            lambda values: self._atualizar(cliente, values),
        )

    def _atualizar(self, original, values):
        cliente = self._cliente_dos_valores(values, original.id, original.estado)
        ClienteService.atualizar_cliente(cliente)
        self.carregar()
        self.status.mostrar("Cliente atualizado com sucesso.", "success")

    def alternar_estado(self):
        cliente_id = self.id_selecionado()
        if cliente_id is None:
            return
        cliente = ClienteService.buscar_cliente(cliente_id, incluir_inativos=True)
        if cliente.estado == "ATIVO":
            ClienteService.remover_cliente(cliente_id)
            mensagem = "Cliente inativado; o histórico foi preservado."
        else:
            ClienteService.reativar_cliente(cliente_id)
            mensagem = "Cliente reativado com sucesso."
        self.carregar()
        self.status.mostrar(mensagem, "success")


class ProdutosView(ListView):
    def __init__(self, master):
        super().__init__(master, "Produtos", "Catálogo, preços e condições de acesso.", (
            ("id", "ID", 60), ("nome", "Produto", 230), ("categoria", "Categoria", 150),
            ("preco", "Preço", 110), ("validade", "Validade", 150),
            ("estado", "Estado", 90),
        ))
        self.adicionar_acao("Novo produto", self.novo, destaque=True)
        self.adicionar_acao("Editar", self.editar)
        self.adicionar_acao("Ativar/Inativar", self.alternar_estado)
        self.table.tree.bind("<Double-1>", lambda _event: self.editar())
        self.carregar()

    FIELDS = (
        ("nome", "Nome *"), ("categoria", "Categoria"), ("preco", "Preço *"),
        ("tipo_validade", "Tipo de validade", "combo", ("VITALICIO", "TEMPORARIO")),
        ("duracao_dias", "Duração em dias (apenas temporário)"),
        ("descricao", "Descrição", "text"),
    )

    def obter_linhas(self, termo):
        produtos = ProdutoService.pesquisar_produtos(termo, apenas_ativos=False)
        return [(p.id, p.nome, formatar_texto(p.categoria), formatar_moeda(p.preco),
                 "Vitalício" if p.tipo_validade == "VITALICIO" else f"{p.duracao_dias} dias",
                 "ATIVO" if p.ativo else "INATIVO") for p in produtos]

    def novo(self):
        self.dialog = FormDialog(
            self, "Novo produto", self.FIELDS,
            {"tipo_validade": "VITALICIO", "preco": "0,00"}, self._criar,
        )

    def _produto_dos_valores(self, values, produto_id=None, ativo=True):
        tipo = values["tipo_validade"]
        duracao = interpretar_inteiro_opcional(values["duracao_dias"], "duração")
        if tipo == "VITALICIO":
            duracao = None
        return Produto(
            id=produto_id, nome=values["nome"], categoria=texto_opcional(values["categoria"]),
            preco=interpretar_decimal(values["preco"], "preço"),
            descricao=texto_opcional(values["descricao"]), tipo_validade=tipo,
            duracao_dias=duracao, ativo=ativo,
        )

    def _criar(self, values):
        ProdutoService.criar_produto(self._produto_dos_valores(values))
        self.carregar()
        self.status.mostrar("Produto criado com sucesso.", "success")

    def editar(self):
        produto_id = self.id_selecionado()
        if produto_id is None:
            return
        produto = ProdutoService.buscar_produto(produto_id)
        initial = {key: getattr(produto, key) or "" for key, *_ in self.FIELDS}
        self.dialog = FormDialog(
            self, "Editar produto", self.FIELDS, initial,
            lambda values: self._atualizar(produto, values),
        )

    def _atualizar(self, original, values):
        produto = self._produto_dos_valores(values, original.id, original.ativo)
        ProdutoService.atualizar_produto(produto)
        self.carregar()
        self.status.mostrar("Produto atualizado com sucesso.", "success")

    def alternar_estado(self):
        produto_id = self.id_selecionado()
        if produto_id is None:
            return
        produto = ProdutoService.buscar_produto(produto_id)
        if produto.ativo:
            ProdutoService.desativar_produto(produto_id)
            mensagem = "Produto inativado; o histórico foi preservado."
        else:
            ProdutoService.reativar_produto(produto_id)
            mensagem = "Produto reativado com sucesso."
        self.carregar()
        self.status.mostrar(mensagem, "success")


class LeadsView(ListView):
    def __init__(self, master):
        super().__init__(master, "Leads", "Oportunidades e evolução do funil comercial.", (
            ("id", "ID", 60), ("nome", "Nome", 210), ("empresa", "Empresa", 160),
            ("contacto", "Contacto", 210), ("origem", "Origem", 120),
            ("produto", "Produto", 170), ("estado", "Estado", 120),
            ("criado", "Criado em", 110),
        ))
        self.adicionar_acao("Novo lead", self.novo, destaque=True)
        self.adicionar_acao("Editar", self.editar)
        self.adicionar_acao("Converter", self.converter)
        self.table.tree.bind("<Double-1>", lambda _event: self.editar())
        self.carregar()

    def obter_linhas(self, termo):
        leads = LeadService.pesquisar_leads(termo=termo)
        produtos = {p.id: p.nome for p in ProdutoService.listar_produtos()}
        return [(l.id, l.nome, formatar_texto(l.empresa),
                 formatar_texto(l.email or l.telefone), formatar_texto(l.origem),
                 formatar_texto(produtos.get(l.produto_interesse_id)),
                 l.estado, formatar_data(l.criado_em)) for l in leads]

    def _opcoes_produtos(self):
        return ("— Sem produto —",) + tuple(
            formatar_opcao_entidade(produto.id, produto.nome)
            for produto in ProdutoService.listar_produtos(apenas_ativos=True)
        )

    def _fields(self):
        return (
            ("nome", "Nome *"), ("empresa", "Empresa"),
            ("telefone", "Telefone"), ("email", "Email"),
            ("origem", "Origem"),
            ("estado", "Estado", "combo", ("NOVO", "CONTACTADO", "QUALIFICADO", "PERDIDO")),
            ("produto_interesse", "Produto de interesse", "combo", self._opcoes_produtos()),
            ("observacoes", "Observações", "text"),
        )

    def _opcao_produto(self, produto_id):
        if produto_id is None:
            return "— Sem produto —"
        produto = ProdutoService.buscar_produto(produto_id)
        return formatar_opcao_entidade(produto.id, produto.nome)

    def _lead_dos_valores(self, values, lead_id=None):
        return Lead(
            id=lead_id, nome=values["nome"], empresa=texto_opcional(values["empresa"]),
            telefone=texto_opcional(values["telefone"]), email=texto_opcional(values["email"]),
            origem=texto_opcional(values["origem"]), estado=values["estado"],
            produto_interesse_id=interpretar_id_opcao(values["produto_interesse"]),
            observacoes=texto_opcional(values["observacoes"]),
        )

    def novo(self):
        self.dialog = FormDialog(
            self, "Novo lead", self._fields(),
            {"estado": "NOVO", "produto_interesse": "— Sem produto —"}, self._criar,
        )

    def _criar(self, values):
        LeadService.criar_lead(self._lead_dos_valores(values))
        self.carregar()
        self.status.mostrar("Lead criado com sucesso.", "success")

    def editar(self):
        lead_id = self.id_selecionado()
        if lead_id is None:
            return
        lead = LeadService.buscar_lead(lead_id)
        if lead.estado == "CONVERTIDO":
            self.status.mostrar("Leads convertidos não podem ser editados.", "error")
            return
        fields = self._fields()
        initial = {
            "nome": lead.nome, "empresa": lead.empresa or "",
            "telefone": lead.telefone or "", "email": lead.email or "",
            "origem": lead.origem or "", "estado": lead.estado,
            "produto_interesse": self._opcao_produto(lead.produto_interesse_id),
            "observacoes": lead.observacoes or "",
        }
        self.dialog = FormDialog(
            self, "Editar lead", fields, initial,
            lambda values: self._atualizar(lead, values),
        )

    def _atualizar(self, original, values):
        atualizado = LeadService.atualizar_lead(
            self._lead_dos_valores(values, original.id)
        )
        if not atualizado:
            raise ValueError("O lead já foi convertido e não pode ser alterado.")
        self.carregar()
        self.status.mostrar("Lead atualizado com sucesso.", "success")

    def converter(self):
        lead_id = self.id_selecionado()
        if lead_id is None:
            return
        lead = LeadService.buscar_lead(lead_id)
        if lead.estado == "CONVERTIDO":
            self.status.mostrar("Este lead já foi convertido em cliente.", "error")
            return
        fields = (
            ("morada", "Morada do cliente"), ("pais", "País"),
            ("tipo_documento", "Tipo de documento"),
            ("numero_documento", "Número do documento"),
            ("observacoes_cliente", "Observações do cliente", "text"),
        )
        initial = {"pais": "Portugal", "observacoes_cliente": lead.observacoes or ""}
        self.dialog = FormDialog(
            self, f"Converter {lead.nome}", fields, initial,
            lambda values: self._converter(lead, values),
        )

    def _converter(self, lead, values):
        cliente_id = LeadService.converter_em_cliente(
            lead_id=lead.id, morada=texto_opcional(values["morada"]),
            pais=values["pais"].strip() or "Portugal",
            tipo_documento=texto_opcional(values["tipo_documento"]),
            numero_documento=texto_opcional(values["numero_documento"]),
            observacoes_cliente=texto_opcional(values["observacoes_cliente"]),
        )
        self.carregar()
        self.status.mostrar(
            f"Lead convertido com sucesso no cliente #{cliente_id}.", "success",
        )


class PedidosView(ListView):
    def __init__(self, master):
        super().__init__(master, "Pedidos", "Histórico de pedidos e respetivos estados.", (
            ("id", "ID", 70), ("referencia", "Referência", 160),
            ("cliente", "Cliente ID", 100), ("data", "Data", 120),
            ("estado", "Estado", 110), ("itens", "Itens", 80), ("total", "Total", 120),
        ))
        self.carregar()

    def obter_linhas(self, termo):
        pedidos = PedidoService.listar_pedidos()
        termo = termo.casefold()
        if termo:
            pedidos = [p for p in pedidos if termo in (p.referencia_externa or "").casefold()
                       or termo in str(p.id)]
        return [(p.id, formatar_texto(p.referencia_externa), p.cliente_id,
                 formatar_data(p.data_pedido), p.estado, len(p.itens),
                 formatar_moeda(p.total)) for p in pedidos]
