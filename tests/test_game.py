from klondike.foundation import FoundationPile
from klondike.game import KlondikeGame
from klondike.stock import StockPile
from klondike.tableau import TableauPile
from klondike.waste import WastePile


def test_new_game_has_seven_tableau_piles():
    game = KlondikeGame()

    assert len(game.tableau) == 7
    assert all(isinstance(pile, TableauPile) for pile in game.tableau)


def test_new_game_has_four_foundation_piles():
    game = KlondikeGame()

    assert len(game.foundations) == 4
    assert all(
        isinstance(pile, FoundationPile)
        for pile in game.foundations
    )


def test_new_game_has_empty_stock():
    game = KlondikeGame()

    assert isinstance(game.stock, StockPile)
    assert game.stock.is_empty()


def test_new_game_has_empty_waste():
    game = KlondikeGame()

    assert isinstance(game.waste, WastePile)
    assert game.waste.is_empty()


def test_new_game_has_empty_tableau_piles():
    game = KlondikeGame()

    assert all(pile.is_empty() for pile in game.tableau)


def test_new_game_has_empty_foundation_piles():
    game = KlondikeGame()

    assert all(pile.is_empty() for pile in game.foundations)