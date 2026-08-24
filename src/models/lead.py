from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.models.cliente import EMAIL_PATTERN, _normalizar_texto_opcional


@dataclass
class Lead:
    id: Optional[int] = None
    nome: str = ""
    empresa: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    origem: Optional[str] = None
    estado: str = "NOVO"
    produto_interesse_id: Optional[int] = None
    cliente_id: Optional[int] = None
    observacoes: Optional[str] = None
    convertido_em: Optional[datetime] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    ESTADOS_VALIDOS = {
        "NOVO",
        "CONTACTADO",
        "QUALIFICADO",
        "CONVERTIDO",
        "PERDIDO",
    }

    def __post_init__(self) -> None:
        if self.id is not None and self.id <= 0:
            raise ValueError("O ID do lead deve ser válido.")

        self.nome = self.nome.strip()
        if not self.nome:
            raise ValueError("O nome do lead é obrigatório.")

        self.empresa = _normalizar_texto_opcional(self.empresa)
        self.telefone = _normalizar_texto_opcional(self.telefone)
        self.origem = _normalizar_texto_opcional(self.origem)
        self.observacoes = _normalizar_texto_opcional(self.observacoes)
        self.estado = self.estado.strip().upper()

        if self.estado not in self.ESTADOS_VALIDOS:
            raise ValueError(
                "O estado deve ser NOVO, CONTACTADO, QUALIFICADO, "
                "CONVERTIDO ou PERDIDO."
            )

        if self.email is not None:
            self.email = self.email.strip().lower() or None
        if self.email is not None and not EMAIL_PATTERN.fullmatch(self.email):
            raise ValueError("O email do lead não é válido.")

        if (
            self.produto_interesse_id is not None
            and self.produto_interesse_id <= 0
        ):
            raise ValueError("O ID do produto de interesse deve ser válido.")
        if self.cliente_id is not None and self.cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser válido.")

        if self.estado == "CONVERTIDO":
            if self.cliente_id is None:
                raise ValueError(
                    "Um lead convertido deve possuir um cliente."
                )
            if self.convertido_em is None:
                raise ValueError(
                    "Um lead convertido deve possuir a data de conversão."
                )
        elif self.cliente_id is not None or self.convertido_em is not None:
            raise ValueError(
                "Apenas leads convertidos podem possuir "
                "cliente e data de conversão."
            )
