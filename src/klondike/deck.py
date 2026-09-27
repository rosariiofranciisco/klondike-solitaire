"""Deck model for Klondike Solitaire."""

import random

from klondike.card import Card, Rank, Suit


class Deck:
    """Represent a standard 52-card deck."""

    def __init__(self) -> None:
        self.cards: list[Card] = [
            Card(suit, rank)
            for suit in Suit
            for rank in Rank
        ]

    def shuffle(self) -> None:
        """Shuffle the cards in the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Card:
        """Remove and return the top card of the deck."""
        if not self.cards:
            raise IndexError("Cannot draw from an empty deck.")

        return self.cards.pop()

    def __len__(self) -> int:
        """Return the number of cards remaining in the deck."""
        return len(self.cards)