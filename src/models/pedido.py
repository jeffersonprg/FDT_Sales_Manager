from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Optional

from src.models.item_pedido import ItemPedido


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass
class Pedido:
    id: Optional[int] = None
    cliente_id: int = 0
    referencia_externa: Optional[str] = None
    data_pedido: datetime = field(default_factory=_agora_utc)
    estado: str = "PENDENTE"
    total: float = 0.0
    observacoes: Optional[str] = None
    pago_em: Optional[datetime] = None
    cancelado_em: Optional[datetime] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    itens: list[ItemPedido] = field(default_factory=list)

    ESTADOS_VALIDOS = {"PENDENTE", "PAGO", "CANCELADO"}

    def __post_init__(self) -> None:
        if self.id is not None and self.id <= 0:
            raise ValueError("O ID do pedido deve ser válido.")
        if isinstance(self.cliente_id, bool) or self.cliente_id <= 0:
            raise ValueError("O pedido deve possuir um cliente válido.")
        if not isinstance(self.data_pedido, datetime):
            raise ValueError("A data do pedido deve ser válida.")

        if self.referencia_externa is not None:
            self.referencia_externa = self.referencia_externa.strip() or None

        if self.observacoes is not None:
            self.observacoes = self.observacoes.strip() or None

        self.estado = self.estado.strip().upper()
        if self.estado not in self.ESTADOS_VALIDOS:
            raise ValueError(
                "O estado deve ser PENDENTE, PAGO ou CANCELADO."
            )

        if isinstance(self.total, bool) or not isinstance(
            self.total,
            (int, float),
        ):
            raise ValueError("O total do pedido deve ser numérico.")

        self.total = round(float(self.total), 2)
        if not isfinite(self.total) or self.total < 0:
            raise ValueError("O total do pedido não pode ser negativo.")

        if self.estado == "PENDENTE":
            if self.pago_em is not None or self.cancelado_em is not None:
                raise ValueError(
                    "Um pedido pendente não pode possuir datas de "
                    "pagamento ou cancelamento."
                )
        elif self.estado == "PAGO":
            self.pago_em = self.pago_em or self.data_pedido
            if self.cancelado_em is not None:
                raise ValueError(
                    "Um pedido pago não pode possuir data de cancelamento."
                )
        else:
            self.cancelado_em = self.cancelado_em or self.data_pedido

        if self.pago_em is not None and self.pago_em < self.data_pedido:
            raise ValueError(
                "A data de pagamento não pode ser anterior à data do pedido."
            )
        if self.cancelado_em is not None:
            data_minima = self.pago_em or self.data_pedido
            if self.cancelado_em < data_minima:
                raise ValueError(
                    "A data de cancelamento não pode ser anterior "
                    "ao pedido ou pagamento."
                )

        if self.itens:
            self.total = self.calcular_total()

    def calcular_total(self) -> float:
        return round(sum(item.subtotal or 0 for item in self.itens), 2)

    def adicionar_item(self, item: ItemPedido) -> None:
        if any(
            item_existente.produto_id == item.produto_id
            for item_existente in self.itens
        ):
            raise ValueError("O produto já foi adicionado ao pedido.")

        self.itens.append(item)
        self.total = self.calcular_total()
