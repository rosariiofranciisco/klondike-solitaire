"""Klondike game model."""

from klondike.card import Rank, Suit
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

    def recycle_waste_to_stock(self) -> None:
        """Move all waste cards back to the stock."""
        while not self.waste.is_empty():
            card = self.waste.remove()
            card.face_up = False
            self.stock.add(card)

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

    def move_tableau_to_tableau(
        self,
        source_index: int,
        card_index: int,
        target_index: int,
    ) -> bool:
        """Move a valid tableau sequence to another tableau."""
        if not 0 <= source_index < len(self.tableau):
            return False

        if not 0 <= target_index < len(self.tableau):
            return False

        if source_index == target_index:
            return False

        source = self.tableau[source_index]
        target = self.tableau[target_index]

        if not source.can_move_sequence(card_index):
            return False

        moving_cards = source.cards[card_index:]
        first_card = moving_cards[0]

        if target.is_empty():
            if first_card.rank != Rank.KING:
                return False
        else:
            target_card = target.peek()

            if target_card.rank != first_card.rank + 1:
                return False

            target_is_red = target_card.suit in (Suit.HEARTS, Suit.DIAMONDS)
            first_is_red = first_card.suit in (Suit.HEARTS, Suit.DIAMONDS)

            if target_is_red == first_is_red:
                return False

        moving_cards = source.cards[card_index:]

        for card in moving_cards:
            target.add(card)

        del source.cards[card_index:]
        source.reveal_top()

        return True

    def move_waste_to_tableau(self, tableau_index: int) -> bool:
        """Move the top waste card to a tableau if valid."""
        if not 0 <= tableau_index < len(self.tableau):
            return False

        if self.waste.is_empty():
            return False

        tableau = self.tableau[tableau_index]
        card = self.waste.peek()

        if tableau.is_empty():
            if card.rank != Rank.KING:
                return False
        else:
            top_card = tableau.peek()

            if top_card.rank != card.rank + 1:
                return False

            top_is_red = top_card.suit in (Suit.HEARTS, Suit.DIAMONDS)
            card_is_red = card.suit in (Suit.HEARTS, Suit.DIAMONDS)

            if top_is_red == card_is_red:
                return False

        tableau.add(self.waste.remove())

        return True

    def move_foundation_to_tableau(
        self,
        foundation_index: int,
        tableau_index: int,
    ) -> bool:
        """Move the top foundation card to a tableau if valid."""
        if not 0 <= foundation_index < len(self.foundations):
            return False

        if not 0 <= tableau_index < len(self.tableau):
            return False

        foundation = self.foundations[foundation_index]
        tableau = self.tableau[tableau_index]

        if foundation.is_empty():
            return False

        card = foundation.peek()

        if tableau.is_empty():
            if card.rank != Rank.KING:
                return False
        else:
            top_card = tableau.peek()

            if top_card.rank != card.rank + 1:
                return False

            top_is_red = top_card.suit in (Suit.HEARTS, Suit.DIAMONDS)
            card_is_red = card.suit in (Suit.HEARTS, Suit.DIAMONDS)

            if top_is_red == card_is_red:
                return False

        tableau.add(foundation.remove())

        return True        

    def is_won(self) -> bool:
        """Return whether all cards have been moved to the foundations."""
        return sum(len(foundation) for foundation in self.foundations) == 52