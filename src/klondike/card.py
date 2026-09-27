"""Card models for Klondike Solitaire."""

from dataclasses import dataclass
from enum import Enum, IntEnum


class Suit(Enum):
    """The four suits in a standard deck."""

    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(IntEnum):
    """The thirteen ranks in a standard deck."""

    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


@dataclass
class Card:
    """Represent a playing card."""

    suit: Suit
    rank: Rank
    face_up: bool = False