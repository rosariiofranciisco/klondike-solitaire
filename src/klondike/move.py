"""Move models for Klondike Solitaire."""

from dataclasses import dataclass
from enum import Enum


class MoveType(Enum):
    """Represent the possible types of moves."""

    STOCK_TO_WASTE = "stock_to_waste"
    WASTE_TO_FOUNDATION = "waste_to_foundation"
    WASTE_TO_TABLEAU = "waste_to_tableau"
    TABLEAU_TO_FOUNDATION = "tableau_to_foundation"
    TABLEAU_TO_TABLEAU = "tableau_to_tableau"
    FOUNDATION_TO_TABLEAU = "foundation_to_tableau"


@dataclass
class Move:
    """Represent a move in a Klondike Solitaire game."""

    move_type: MoveType
    source_index: int | None = None
    card_index: int | None = None
    target_index: int | None = None