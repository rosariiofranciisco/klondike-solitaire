import pytest

from klondike.card import Card, Rank, Suit
from klondike.deck import Deck


def test_deck_has_52_cards():
    deck = Deck()

    assert len(deck) == 52


def test_deck_contains_all_card_combinations():
    deck = Deck()

    actual_cards = {(card.suit, card.rank) for card in deck.cards}
    expected_cards = {(suit, rank) for suit in Suit for rank in Rank}

    assert actual_cards == expected_cards


def test_drawing_card_reduces_deck_size():
    deck = Deck()

    card = deck.draw()

    assert isinstance(card, Card)
    assert len(deck) == 51


def test_drawing_from_empty_deck_raises_error():
    deck = Deck()

    for _ in range(52):
        deck.draw()

    with pytest.raises(IndexError):
        deck.draw()


def test_shuffle_keeps_all_52_cards():
    deck = Deck()
    original_cards = {(card.suit, card.rank) for card in deck.cards}

    deck.shuffle()

    shuffled_cards = {(card.suit, card.rank) for card in deck.cards}

    assert len(deck) == 52
    assert shuffled_cards == original_cards