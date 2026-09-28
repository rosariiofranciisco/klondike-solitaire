"""Klondike game model."""

from klondike.card import Rank
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

    def move_waste_to_foundation(self, foundation_index: int) -> bool:
        """Move the top waste card to a foundation if the move is valid."""
        if self.waste.is_empty():
            return False

        if not 0 <= foundation_index < len(self.foundations):
            return False

        card = self.waste.peek()
        foundation = self.foundations[foundation_index]

        if foundation.is_empty():
            if card.rank != 1:
                return False
        else:
            top_card = foundation.peek()

            if card.suit != top_card.suit:
                return False

            if card.rank != top_card.rank + 1:
                return False

        foundation.add(self.waste.remove())
        return True

    def move_tableau_to_foundation(
        self,
        tableau_index: int,
        foundation_index: int,
    ) -> bool:
        """Move the top tableau card to a foundation if valid."""
        if not 0 <= tableau_index < len(self.tableau):
            return False

        if not 0 <= foundation_index < len(self.foundations):
            return False

        tableau = self.tableau[tableau_index]

        if tableau.is_empty():
            return False

        card = tableau.peek()
        foundation = self.foundations[foundation_index]

        if foundation.is_empty():
            if card.rank != Rank.ACE:
                return False
        else:
            top_card = foundation.peek()

            if card.suit != top_card.suit:
                return False

            if card.rank != top_card.rank + 1:
                return False

        foundation.add(tableau.remove())
        tableau.reveal_top()

        return True