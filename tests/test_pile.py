import pytest

from klondike.card import Card, Rank, Suit
from klondike.pile import Pile


def test_new_pile_is_empty():
    pile = Pile()

    assert pile.is_empty()
    assert len(pile) == 0


def test_add_card_increases_pile_size():
    pile = Pile()
    card = Card(Suit.HEARTS, Rank.ACE)

    pile.add(card)

    assert len(pile) == 1
    assert not pile.is_empty()


def test_peek_returns_top_card_without_removing_it():
    pile = Pile()
    first_card = Card(Suit.HEARTS, Rank.ACE)
    second_card = Card(Suit.SPADES, Rank.KING)

    pile.add(first_card)
    pile.add(second_card)

    assert pile.peek() == second_card
    assert len(pile) == 2


def test_remove_returns_top_card_and_reduces_size():
    pile = Pile()
    first_card = Card(Suit.HEARTS, Rank.ACE)
    second_card = Card(Suit.SPADES, Rank.KING)

    pile.add(first_card)
    pile.add(second_card)

    removed_card = pile.remove()

    assert removed_card == second_card
    assert len(pile) == 1
    assert pile.peek() == first_card


def test_remove_from_empty_pile_raises_error():
    pile = Pile()

    with pytest.raises(IndexError):
        pile.remove()


def test_peek_at_empty_pile_raises_error():
    pile = Pile()

    with pytest.raises(IndexError):
        pile.peek()