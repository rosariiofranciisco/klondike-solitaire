from klondike.card import Card, Rank, Suit
from klondike.pile import Pile
from klondike.stock import StockPile


def test_new_stock_is_empty():
    stock = StockPile()

    assert stock.is_empty()
    assert len(stock) == 0


def test_stock_inherits_from_pile():
    stock = StockPile()

    assert isinstance(stock, Pile)


def test_stock_can_add_and_remove_cards():
    stock = StockPile()
    card = Card(Suit.HEARTS, Rank.ACE)

    stock.add(card)

    assert len(stock) == 1
    assert stock.peek() == card
    assert stock.remove() == card
    assert stock.is_empty()