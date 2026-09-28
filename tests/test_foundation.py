from klondike.card import Card, Rank, Suit
from klondike.foundation import FoundationPile
from klondike.pile import Pile


def test_new_foundation_is_empty():
    foundation = FoundationPile()

    assert foundation.is_empty()
    assert len(foundation) == 0


def test_foundation_inherits_from_pile():
    foundation = FoundationPile()

    assert isinstance(foundation, Pile)


def test_foundation_can_add_and_remove_cards():
    foundation = FoundationPile()
    card = Card(Suit.HEARTS, Rank.ACE)

    foundation.add(card)

    assert len(foundation) == 1
    assert foundation.peek() == card
    assert foundation.remove() == card
    assert foundation.is_empty()