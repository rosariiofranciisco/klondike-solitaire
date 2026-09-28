from klondike.card import Card, Rank, Suit
from klondike.pile import Pile
from klondike.waste import WastePile


def test_new_waste_is_empty():
    waste = WastePile()

    assert waste.is_empty()
    assert len(waste) == 0


def test_waste_inherits_from_pile():
    waste = WastePile()

    assert isinstance(waste, Pile)


def test_waste_can_add_and_remove_cards():
    waste = WastePile()
    card = Card(Suit.HEARTS, Rank.ACE)

    waste.add(card)

    assert len(waste) == 1
    assert waste.peek() == card
    assert waste.remove() == card
    assert waste.is_empty()