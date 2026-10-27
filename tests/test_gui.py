
import pygame
import pytest

from klondike.card import Card, Rank, Suit
from klondike.config import (
    CARD_HEIGHT,
    CARD_SLOT_GAP,
    CARD_WIDTH,
    COLUMN_GAP,
    FOUNDATION_COUNT,
    MARGIN_X,
    TABLEAU_CARD_OFFSET,
    TABLEAU_Y,
    TOP_ROW_Y,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from klondike.gui import KlondikeGUI
from klondike.move import MoveType


@pytest.fixture
def gui(monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    instance = KlondikeGUI()
    yield instance
    pygame.quit()


def test_gui_dimensions():
    assert WINDOW_WIDTH == 900
    assert WINDOW_HEIGHT == 650
    assert CARD_WIDTH == 70
    assert CARD_HEIGHT == 100


def test_click_stock_draws_card(gui):
    stock_size = len(gui.game.stock)
    card = gui.game.stock.peek()

    gui._handle_left_click((MARGIN_X + 10, TOP_ROW_Y + 10))

    assert len(gui.game.stock) == stock_size - 1
    assert gui.game.waste.peek() is card
    assert card.face_up


def test_click_empty_stock_recycles_waste(gui):
    stock_position = (MARGIN_X + 10, TOP_ROW_Y + 10)

    while not gui.game.stock.is_empty():
        gui._handle_left_click(stock_position)

    waste_size = len(gui.game.waste)
    assert waste_size > 0

    gui._handle_left_click(stock_position)

    assert gui.game.stock.is_empty() is False
    assert len(gui.game.stock) == waste_size
    assert gui.game.waste.is_empty()
    assert all(not card.face_up for card in gui.game.stock.cards)

def test_click_waste_then_tableau_moves_card(gui):
    gui.game.stock.cards.clear()
    gui.game.waste.cards.clear()

    for pile in gui.game.tableau:
        pile.cards.clear()

    target_card = Card(Suit.HEARTS, Rank.SEVEN, face_up=True)
    moving_card = Card(Suit.CLUBS, Rank.SIX, face_up=True)

    gui.game.tableau[0].add(target_card)
    gui.game.waste.add(moving_card)

    waste_x = MARGIN_X + CARD_WIDTH + CARD_SLOT_GAP + 10
    card_y = TOP_ROW_Y + 10

    gui._handle_left_click((waste_x, card_y))

    assert gui.selected_source is not None
    assert gui.selected_source[0] == MoveType.WASTE_TO_TABLEAU

    tableau_x = MARGIN_X + 10
    tableau_y = TABLEAU_Y + 10

    gui._handle_left_click((tableau_x, tableau_y))

    assert gui.game.waste.is_empty()
    assert gui.game.tableau[0].cards == [target_card, moving_card]
    assert gui.selected_source is None

def test_click_tableau_moves_card_and_reveals_source_top(gui):
    gui.game.stock.cards.clear()
    gui.game.waste.cards.clear()

    for pile in gui.game.tableau:
        pile.cards.clear()

    hidden_card = Card(Suit.HEARTS, Rank.FIVE)
    moving_card = Card(Suit.CLUBS, Rank.SIX, face_up=True)
    target_card = Card(Suit.DIAMONDS, Rank.SEVEN, face_up=True)

    gui.game.tableau[0].add(hidden_card)
    gui.game.tableau[0].add(moving_card)
    gui.game.tableau[1].add(target_card)

    source_x = MARGIN_X + 10
    source_y = TABLEAU_Y + TABLEAU_CARD_OFFSET + 10

    target_x = MARGIN_X + CARD_WIDTH + COLUMN_GAP + 10
    target_y = TABLEAU_Y + 10

    gui._handle_left_click((source_x, source_y))

    assert gui.selected_source is not None
    assert gui.selected_source[0] == MoveType.TABLEAU_TO_TABLEAU

    gui._handle_left_click((target_x, target_y))

    assert gui.game.tableau[0].cards == [hidden_card]
    assert hidden_card.face_up
    assert gui.game.tableau[1].cards == [target_card, moving_card]
    assert gui.selected_source is None


def test_click_foundation_then_tableau_moves_card(gui):
    gui.game.stock.cards.clear()
    gui.game.waste.cards.clear()

    for pile in gui.game.tableau:
        pile.cards.clear()

    for foundation in gui.game.foundations:
        foundation.cards.clear()

    moving_card = Card(Suit.CLUBS, Rank.SIX, face_up=True)
    target_card = Card(Suit.DIAMONDS, Rank.SEVEN, face_up=True)

    gui.game.foundations[0].add(moving_card)
    gui.game.tableau[1].add(target_card)

    foundation_start_x = (
        WINDOW_WIDTH
        - MARGIN_X
        - (
            FOUNDATION_COUNT * CARD_WIDTH
            + (FOUNDATION_COUNT - 1) * CARD_SLOT_GAP
        )
    )

    foundation_x = foundation_start_x + 10
    foundation_y = TOP_ROW_Y + 10

    tableau_x = MARGIN_X + CARD_WIDTH + COLUMN_GAP + 10
    tableau_y = TABLEAU_Y + 10

    gui._handle_left_click((foundation_x, foundation_y))

    assert gui.selected_source is not None
    assert gui.selected_source[0] == MoveType.FOUNDATION_TO_TABLEAU
    assert gui.selected_source[1] == 0

    gui._handle_left_click((tableau_x, tableau_y))

    assert gui.game.foundations[0].is_empty()
    assert gui.game.tableau[1].cards == [target_card, moving_card]
    assert gui.selected_source is None


def test_selected_tableau_card_is_highlighted(gui, monkeypatch):
    for pile in gui.game.tableau:
        pile.cards.clear()

    first_card = Card(Suit.HEARTS, Rank.FIVE)
    selected_card = Card(Suit.CLUBS, Rank.SIX, face_up=True)

    gui.game.tableau[0].add(first_card)
    gui.game.tableau[0].add(selected_card)

    gui.selected_source = (
        MoveType.TABLEAU_TO_TABLEAU,
        0,
        1,
    )

    highlighted_positions = []

    monkeypatch.setattr(
        gui,
        "_draw_selection",
        lambda x, y: highlighted_positions.append((x, y)),
    )

    gui._draw_tableau()

    assert highlighted_positions == [
        (MARGIN_X, TABLEAU_Y + TABLEAU_CARD_OFFSET)
    ]


def test_selected_foundation_is_highlighted(gui, monkeypatch):
    moving_card = Card(Suit.CLUBS, Rank.SIX, face_up=True)
    gui.game.foundations[0].add(moving_card)

    gui.selected_source = (
        MoveType.FOUNDATION_TO_TABLEAU,
        0,
        None,
    )

    highlighted_positions = []

    monkeypatch.setattr(
        gui,
        "_draw_selection",
        lambda x, y: highlighted_positions.append((x, y)),
    )

    gui._draw_top_row()

    foundation_start_x = (
        WINDOW_WIDTH
        - MARGIN_X
        - (
            FOUNDATION_COUNT * CARD_WIDTH
            + (FOUNDATION_COUNT - 1) * CARD_SLOT_GAP
        )
    )

    assert highlighted_positions == [
        (foundation_start_x, TOP_ROW_Y)
    ]
