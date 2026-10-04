"""Tableau pile model for Klondike Solitaire."""

from klondike.card import RED_SUITS
from klondike.pile import Pile


class TableauPile(Pile):
    """Represent a pile of cards in the Klondike tableau."""

    def reveal_top(self) -> None:
        """Reveal the top card if it is face-down."""
        if not self.cards:
            return

        self.cards[-1].face_up = True

    def can_move_sequence(self, card_index: int) -> bool:
        """Return whether the sequence from card_index is valid to move."""
        if not 0 <= card_index < len(self.cards):
            return False

        sequence = self.cards[card_index:]

        if not all(card.face_up for card in sequence):
            return False

        for current, next_card in zip(
            sequence,
            sequence[1:],
            strict=False,
        ):
            if current.rank != next_card.rank + 1:
                return False

            current_is_red = current.suit in RED_SUITS
            next_is_red = next_card.suit in RED_SUITS

            if current_is_red == next_is_red:
                return False

        return True