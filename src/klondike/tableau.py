"""Tableau pile model for Klondike Solitaire."""

from klondike.pile import Pile


class TableauPile(Pile):
    """Represent a pile of cards in the Klondike tableau."""

    def reveal_top(self) -> None:
        """Reveal the top card if it is face-down."""
        if not self.cards:
            return

        self.cards[-1].face_up = True