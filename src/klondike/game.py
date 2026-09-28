"""Klondike game model."""

from klondike.deck import Deck
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

    def start_new_game(self) -> None:
        """Create and deal a new Klondike game."""
        deck = Deck()
        deck.shuffle()

        for tableau_index in range(7):
            for _ in range(tableau_index + 1):
                self.tableau[tableau_index].add(deck.draw())

            self.tableau[tableau_index].reveal_top()

        while len(deck) > 0:
            self.stock.add(deck.draw())

    def draw_from_stock(self) -> None:
        """Move one card from the stock to the waste."""
        if self.stock.is_empty():
            return

        card = self.stock.remove()
        card.face_up = True
        self.waste.add(card) 