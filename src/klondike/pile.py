"""Pile model for Klondike Solitaire."""

from klondike.card import Card


class Pile:
    """Represent an ordered collection of cards."""

    def __init__(self) -> None:
        self.cards: list[Card] = []

    def add(self, card: Card) -> None:
        """Add a card to the top of the pile."""
        self.cards.append(card)

    def remove(self) -> Card:
        """Remove and return the top card of the pile."""
        if not self.cards:
            raise IndexError("Cannot remove from an empty pile.")

        return self.cards.pop()

    def peek(self) -> Card:
        """Return the top card without removing it."""
        if not self.cards:
            raise IndexError("Cannot peek at an empty pile.")

        return self.cards[-1]

    def is_empty(self) -> bool:
        """Return whether the pile contains no cards."""
        return not self.cards

    def __len__(self) -> int:
        """Return the number of cards in the pile."""
        return len(self.cards)