from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Optional


@dataclass
class ItemPedido:
    id: Optional[int] = None
    pedido_id: Optional[int] = None
    produto_id: int = 0
    quantidade: int = 1
    preco_unitario: float = 0.0
    subtotal: Optional[float] = None
    inicio_acesso: Optional[date] = None
    fim_acesso: Optional[date] = None

    def __post_init__(self) -> None:
        if self.id is not None and self.id <= 0:
            raise ValueError("O ID do item deve ser válido.")
        if self.pedido_id is not None and self.pedido_id <= 0:
            raise ValueError("O ID do pedido deve ser válido.")
        if isinstance(self.produto_id, bool) or self.produto_id <= 0:
            raise ValueError("O ID do produto deve ser válido.")
        if (
            isinstance(self.quantidade, bool)
            or not isinstance(self.quantidade, int)
            or self.quantidade <= 0
        ):
            raise ValueError("A quantidade deve ser superior a zero.")
        if isinstance(self.preco_unitario, bool) or not isinstance(
            self.preco_unitario,
            (int, float),
        ):
            raise ValueError("O preço unitário deve ser numérico.")

        self.preco_unitario = round(float(self.preco_unitario), 2)
        if not isfinite(self.preco_unitario) or self.preco_unitario < 0:
            raise ValueError("O preço unitário não pode ser negativo.")

        subtotal_calculado = round(
            self.quantidade * self.preco_unitario,
            2,
        )

        if self.subtotal is None:
            self.subtotal = subtotal_calculado
        elif round(float(self.subtotal), 2) != subtotal_calculado:
            raise ValueError(
                "O subtotal deve corresponder à quantidade "
                "multiplicada pelo preço unitário."
            )
        else:
            self.subtotal = subtotal_calculado

        if self.fim_acesso is not None and self.inicio_acesso is None:
            raise ValueError(
                "A data de início é obrigatória quando existe uma data de fim."
            )
        if (
            self.inicio_acesso is not None
            and self.fim_acesso is not None
            and self.fim_acesso < self.inicio_acesso
        ):
            raise ValueError(
                "A data de fim não pode ser anterior à data de início."
            )
