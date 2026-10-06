"""Klondike game model."""

from copy import deepcopy

from klondike.card import RED_SUITS, Rank
from klondike.deck import Deck
from klondike.foundation import FoundationPile
from klondike.move import Move, MoveType
from klondike.state import GameState
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
        self.history: list[GameState] = []

    def _create_snapshot(self) -> GameState:
        """Create an independent snapshot of the current game state."""
        return GameState(
            tableau=deepcopy(
                [pile.cards for pile in self.tableau]
            ),
            foundations=deepcopy(
                [pile.cards for pile in self.foundations]
            ),
            stock=deepcopy(self.stock.cards),
            waste=deepcopy(self.waste.cards),
        )

    def _restore_snapshot(self, state: GameState) -> None:
        """Restore the game state from a snapshot."""
        for pile, cards in zip(
            self.tableau,
            state.tableau,
            strict=False,
        ):
            pile.cards = deepcopy(cards)

        for pile, cards in zip(
            self.foundations,
            state.foundations,
            strict=False,
        ):
            pile.cards = deepcopy(cards)

        self.stock.cards = deepcopy(state.stock)
        self.waste.cards = deepcopy(state.waste)

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

        self.history.clear()

    def draw_from_stock(self) -> bool:
        """Move one card from the stock to the waste if possible."""
        if self.stock.is_empty():
            return False

        card = self.stock.remove()
        card.face_up = True
        self.waste.add(card)

        return True

    def recycle_waste_to_stock(self) -> None:
        """Move all waste cards back to the stock."""
        while not self.waste.is_empty():
            card = self.waste.remove()
            card.face_up = False
            self.stock.add(card)

    def can_move_waste_to_foundation(self, foundation_index: int) -> bool:
        """Return whether the top waste card can move to a foundation."""
        if not 0 <= foundation_index < len(self.foundations):
            return False

        if self.waste.is_empty():
            return False

        card = self.waste.peek()
        foundation = self.foundations[foundation_index]

        if foundation.is_empty():
            return card.rank == Rank.ACE

        top_card = foundation.peek()

        return (
            card.suit == top_card.suit
            and card.rank == top_card.rank + 1
        )

    def move_waste_to_foundation(self, foundation_index: int) -> bool:
        """Move the top waste card to a foundation if the move is valid."""
        if not self.can_move_waste_to_foundation(foundation_index):
            return False

        foundation = self.foundations[foundation_index]

        foundation.add(self.waste.remove())
        return True

    def can_move_tableau_to_foundation(
        self,
        tableau_index: int,
        foundation_index: int,
    ) -> bool:
        """Return whether the top tableau card can move to a foundation."""
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
            return card.rank == Rank.ACE

        top_card = foundation.peek()

        return (
            card.suit == top_card.suit
            and card.rank == top_card.rank + 1
        )

    def move_tableau_to_foundation(
        self,
        tableau_index: int,
        foundation_index: int,
    ) -> bool:
        """Move the top tableau card to a foundation if valid."""
        if not self.can_move_tableau_to_foundation(
            tableau_index,
            foundation_index,
        ):
            return False

        tableau = self.tableau[tableau_index]
        foundation = self.foundations[foundation_index]

        foundation.add(tableau.remove())
        tableau.reveal_top()

        return True

    def can_move_tableau_to_tableau(
        self,
        source_index: int,
        card_index: int,
        target_index: int,
    ) -> bool:
        """Return whether a tableau sequence can move to another tableau."""
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

        first_card = source.cards[card_index]

        if target.is_empty():
            return first_card.rank == Rank.KING

        target_card = target.peek()

        if target_card.rank != first_card.rank + 1:
            return False

        target_is_red = target_card.suit in RED_SUITS
        first_is_red = first_card.suit in RED_SUITS

        return target_is_red != first_is_red

    def move_tableau_to_tableau(
        self,
        source_index: int,
        card_index: int,
        target_index: int,
    ) -> bool:
        """Move a valid tableau sequence to another tableau."""
        if not self.can_move_tableau_to_tableau(
            source_index,
            card_index,
            target_index,
        ):
            return False

        source = self.tableau[source_index]
        target = self.tableau[target_index]

        moving_cards = source.cards[card_index:]

        for card in moving_cards:
            target.add(card)

        del source.cards[card_index:]
        source.reveal_top()

        return True

    def can_move_waste_to_tableau(self, tableau_index: int) -> bool:
        """Return whether the top waste card can move to a tableau."""
        if not 0 <= tableau_index < len(self.tableau):
            return False

        if self.waste.is_empty():
            return False

        tableau = self.tableau[tableau_index]
        card = self.waste.peek()

        if tableau.is_empty():
            return card.rank == Rank.KING

        top_card = tableau.peek()

        if top_card.rank != card.rank + 1:
            return False

        top_is_red = top_card.suit in RED_SUITS
        card_is_red = card.suit in RED_SUITS

        return top_is_red != card_is_red

    def move_waste_to_tableau(self, tableau_index: int) -> bool:
        """Move the top waste card to a tableau if valid."""
        if not self.can_move_waste_to_tableau(tableau_index):
            return False

        tableau = self.tableau[tableau_index]
        tableau.add(self.waste.remove())

        return True

    def can_move_foundation_to_tableau(
        self,
        foundation_index: int,
        tableau_index: int,
    ) -> bool:
        """Return whether the top foundation card can move to a tableau."""
        if not 0 <= foundation_index < len(self.foundations):
            return False

        if not 0 <= tableau_index < len(self.tableau):
            return False

        foundation = self.foundations[foundation_index]

        if foundation.is_empty():
            return False

        tableau = self.tableau[tableau_index]
        card = foundation.peek()

        if tableau.is_empty():
            return card.rank == Rank.KING

        top_card = tableau.peek()

        if top_card.rank != card.rank + 1:
            return False

        top_is_red = top_card.suit in RED_SUITS
        card_is_red = card.suit in RED_SUITS

        return top_is_red != card_is_red

    def move_foundation_to_tableau(
        self,
        foundation_index: int,
        tableau_index: int,
    ) -> bool:
        """Move the top foundation card to a tableau if valid."""
        if not self.can_move_foundation_to_tableau(
            foundation_index,
            tableau_index,
        ):
            return False

        foundation = self.foundations[foundation_index]
        tableau = self.tableau[tableau_index]

        tableau.add(foundation.remove())

        return True       

    def is_won(self) -> bool:
        """Return whether all cards have been moved to the foundations."""
        return sum(len(foundation) for foundation in self.foundations) == 52

    def is_game_over(self) -> bool:
        """Return whether the game has ended without a win."""
        if self.is_won():
            return True

        if not self.stock.is_empty():
            return False

        if not self.waste.is_empty():
            return False

        for tableau_index in range(len(self.tableau)):
            for foundation_index in range(len(self.foundations)):
                if self.can_move_tableau_to_foundation(
                    tableau_index,
                    foundation_index,
                ):
                    return False

        for source_index in range(len(self.tableau)):
            source = self.tableau[source_index]

            for card_index in range(len(source)):
                for target_index in range(len(self.tableau)):
                    if self.can_move_tableau_to_tableau(
                        source_index,
                        card_index,
                        target_index,
                    ):
                        return False

        for foundation_index in range(len(self.foundations)):
            for tableau_index in range(len(self.tableau)):
                if self.can_move_foundation_to_tableau(
                    foundation_index,
                    tableau_index,
                ):
                    return False

        return True

    def execute_move(self, move: Move) -> bool:
        """Execute a move if it is valid and record its previous state."""
        snapshot = self._create_snapshot()

        if move.move_type == MoveType.STOCK_TO_WASTE:
            result = self.draw_from_stock()

        elif move.move_type == MoveType.WASTE_TO_FOUNDATION:
            if move.target_index is None:
                return False

            result = self.move_waste_to_foundation(
                move.target_index,
            )

        elif move.move_type == MoveType.WASTE_TO_TABLEAU:
            if move.target_index is None:
                return False

            result = self.move_waste_to_tableau(
                move.target_index,
            )

        elif move.move_type == MoveType.TABLEAU_TO_FOUNDATION:
            if move.source_index is None or move.target_index is None:
                return False

            result = self.move_tableau_to_foundation(
                move.source_index,
                move.target_index,
            )

        elif move.move_type == MoveType.TABLEAU_TO_TABLEAU:
            if (
                move.source_index is None
                or move.card_index is None
                or move.target_index is None
            ):
                return False

            result = self.move_tableau_to_tableau(
                move.source_index,
                move.card_index,
                move.target_index,
            )

        elif move.move_type == MoveType.FOUNDATION_TO_TABLEAU:
            if move.source_index is None or move.target_index is None:
                return False

            result = self.move_foundation_to_tableau(
                move.source_index,
                move.target_index,
            )

        else:
            return False

        if result:
            self.history.append(snapshot)

        return result

    def undo(self) -> bool:
        """Undo the most recent successful move."""
        if not self.history:
            return False

        state = self.history.pop()
        self._restore_snapshot(state)

        return True