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

def test_start_new_game_deals_correct_number_of_cards():
    game = KlondikeGame()

    game.start_new_game()

    assert [len(pile) for pile in game.tableau] == [1, 2, 3, 4, 5, 6, 7]
    assert len(game.stock) == 24
    assert len(game.waste) == 0
    assert all(len(pile) == 0 for pile in game.foundations)


def test_start_new_game_has_52_cards_in_total():
    game = KlondikeGame()

    game.start_new_game()

    tableau_cards = sum(len(pile) for pile in game.tableau)
    foundation_cards = sum(len(pile) for pile in game.foundations)

    total_cards = (
        tableau_cards
        + len(game.stock)
        + len(game.waste)
        + foundation_cards
    )

    assert total_cards == 52


def test_start_new_game_reveals_only_top_tableau_cards():
    game = KlondikeGame()

    game.start_new_game()

    for pile in game.tableau:
        assert pile.peek().face_up is True

        for card in pile.cards[:-1]:
            assert card.face_up is False

def test_start_new_game_has_all_52_unique_cards():
    game = KlondikeGame()

    game.start_new_game()

    cards = []

    for pile in game.tableau:
        cards.extend(pile.cards)

    cards.extend(game.stock.cards)
    cards.extend(game.waste.cards)

    for pile in game.foundations:
        cards.extend(pile.cards)

    card_combinations = {(card.suit, card.rank) for card in cards}

    assert len(cards) == 52
    assert len(card_combinations) == 52

def test_draw_from_stock_moves_one_card_to_waste():
    game = KlondikeGame()
    game.start_new_game()

    game.draw_from_stock()

    assert len(game.stock) == 23
    assert len(game.waste) == 1
    assert game.waste.peek().face_up is True


def test_draw_from_stock_moves_the_top_stock_card():
    game = KlondikeGame()
    game.start_new_game()

    stock_top_card = game.stock.peek()

    game.draw_from_stock()

    assert game.waste.peek() == stock_top_card


def test_draw_from_empty_stock_does_nothing():
    game = KlondikeGame()

    game.draw_from_stock()

    assert game.stock.is_empty()
    assert game.waste.is_empty()