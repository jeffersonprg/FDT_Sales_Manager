from dataclasses import dataclass
from math import isfinite
from typing import Optional


def _normalizar_texto_opcional(valor: Optional[str]) -> Optional[str]:
    if valor is None:
        return None

    normalizado = valor.strip()
    return normalizado or None


@dataclass
class Produto:
    id: Optional[int] = None
    nome: str = ""
    categoria: Optional[str] = None
    preco: float = 0.0
    descricao: Optional[str] = None
    tipo_validade: str = "VITALICIO"
    duracao_dias: Optional[int] = None
    ativo: bool = True

    def __post_init__(self) -> None:
        if self.id is not None and self.id <= 0:
            raise ValueError("O ID do produto deve ser válido.")

        self.nome = self.nome.strip()
        self.categoria = _normalizar_texto_opcional(self.categoria)
        self.descricao = _normalizar_texto_opcional(self.descricao)
        self.tipo_validade = self.tipo_validade.strip().upper()

        if not self.nome:
            raise ValueError("O nome do produto é obrigatório.")

        if isinstance(self.preco, bool) or not isinstance(
            self.preco,
            (int, float),
        ):
            raise ValueError("O preço do produto deve ser numérico.")

        self.preco = round(float(self.preco), 2)
        if not isfinite(self.preco) or self.preco < 0:
            raise ValueError("O preço do produto não pode ser negativo.")

        if not isinstance(self.ativo, bool):
            raise ValueError("O estado ativo do produto deve ser booleano.")

        if self.tipo_validade not in ("TEMPORARIO", "VITALICIO"):
            raise ValueError(
                "O tipo de validade deve ser TEMPORARIO ou VITALICIO."
            )

        if self.tipo_validade == "TEMPORARIO":
            if (
                isinstance(self.duracao_dias, bool)
                or not isinstance(self.duracao_dias, int)
                or self.duracao_dias <= 0
            ):
                raise ValueError(
                    "Produtos temporários devem ter duração superior a zero."
                )

        if self.tipo_validade == "VITALICIO" and self.duracao_dias is not None:
            raise ValueError(
                "Produtos vitalícios não devem ter duração em dias."
            )
