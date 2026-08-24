from datetime import datetime

import pytest

from src.models.lead import Lead


def test_criar_lead_novo():
    lead = Lead(
        nome="  Maria Silva  ",
        email="  MARIA@EMAIL.PT  ",
        origem="Instagram"
    )

    assert lead.nome == "Maria Silva"
    assert lead.email == "maria@email.pt"
    assert lead.estado == "NOVO"
    assert lead.cliente_id is None
    assert lead.convertido_em is None


def test_lead_normaliza_estado():
    lead = Lead(
        nome="João Costa",
        estado="qualificado"
    )

    assert lead.estado == "QUALIFICADO"


def test_lead_nao_aceita_nome_vazio():
    with pytest.raises(
        ValueError,
        match="O nome do lead é obrigatório"
    ):
        Lead(nome="   ")


def test_lead_nao_aceita_estado_invalido():
    with pytest.raises(
        ValueError,
        match="O estado deve ser"
    ):
        Lead(
            nome="Lead inválido",
            estado="EM_ANALISE"
        )


def test_lead_nao_aceita_produto_invalido():
    with pytest.raises(
        ValueError,
        match="O ID do produto de interesse deve ser válido"
    ):
        Lead(
            nome="Lead Produto",
            produto_interesse_id=0
        )


def test_lead_convertido_valido():
    data_conversao = datetime(2026, 8, 2, 18, 30)

    lead = Lead(
        nome="Lead Convertido",
        estado="CONVERTIDO",
        cliente_id=1,
        convertido_em=data_conversao
    )

    assert lead.estado == "CONVERTIDO"
    assert lead.cliente_id == 1
    assert lead.convertido_em == data_conversao


def test_lead_convertido_exige_cliente():
    with pytest.raises(
        ValueError,
        match="deve possuir um cliente"
    ):
        Lead(
            nome="Lead sem cliente",
            estado="CONVERTIDO",
            convertido_em=datetime.now()
        )


def test_lead_convertido_exige_data():
    with pytest.raises(
        ValueError,
        match="deve possuir a data de conversão"
    ):
        Lead(
            nome="Lead sem data",
            estado="CONVERTIDO",
            cliente_id=1
        )


def test_lead_nao_convertido_nao_aceita_dados_de_conversao():
    with pytest.raises(
        ValueError,
        match="Apenas leads convertidos"
    ):
        Lead(
            nome="Lead Novo",
            estado="NOVO",
            cliente_id=1,
            convertido_em=datetime.now()
        )