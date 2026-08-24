import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalizar_texto_opcional(valor: Optional[str]) -> Optional[str]:
    if valor is None:
        return None

    normalizado = valor.strip()
    return normalizado or None


@dataclass
class Cliente:
    id: Optional[int] = None
    nome: str = ""
    empresa: Optional[str] = None
    morada: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    pais: str = "Portugal"
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    estado: str = "ATIVO"
    observacoes: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    ESTADOS_VALIDOS = {"ATIVO", "INATIVO"}

    def __post_init__(self) -> None:
        if self.id is not None and self.id <= 0:
            raise ValueError("O ID do cliente deve ser válido.")

        self.nome = self.nome.strip()
        if not self.nome:
            raise ValueError("O nome do cliente é obrigatório.")

        self.empresa = _normalizar_texto_opcional(self.empresa)
        self.morada = _normalizar_texto_opcional(self.morada)
        self.telefone = _normalizar_texto_opcional(self.telefone)
        self.tipo_documento = _normalizar_texto_opcional(
            self.tipo_documento
        )
        self.numero_documento = _normalizar_texto_opcional(
            self.numero_documento
        )
        self.observacoes = _normalizar_texto_opcional(self.observacoes)

        self.pais = self.pais.strip() or "Portugal"
        self.estado = self.estado.strip().upper()

        if self.estado not in self.ESTADOS_VALIDOS:
            raise ValueError(
                "O estado do cliente deve ser ATIVO ou INATIVO."
            )

        if self.tipo_documento is not None:
            self.tipo_documento = self.tipo_documento.upper()

        if self.email is not None:
            self.email = self.email.strip().lower() or None

        if self.email is not None and not EMAIL_PATTERN.fullmatch(self.email):
            raise ValueError("O email do cliente não é válido.")
