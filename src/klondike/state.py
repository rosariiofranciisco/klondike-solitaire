"""Game state models for Klondike Solitaire."""

from dataclasses import dataclass

from klondike.card import Card


@dataclass
class GameState:
    """Represent a snapshot of a Klondike Solitaire game state."""

    tableau: list[list[Card]]
    foundations: list[list[Card]]
    stock: list[Card]
    waste: list[Card]
