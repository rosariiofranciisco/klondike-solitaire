"""Klondike game model."""

from klondike.foundation import FoundationPile
from klondike.stock import StockPile
from klondike.tableau import TableauPile
from klondike.waste import WastePile


class KlondikeGame:
    """Represent the state of a Klondike Solitaire game."""

    def __init__(self) -> None:
        self.tableau: list[TableauPile] = [
            TableauPile() for _ in range(7)
        ]
        self.foundations: list[FoundationPile] = [
            FoundationPile() for _ in range(4)
        ]
        self.stock = StockPile()
        self.waste = WastePile()