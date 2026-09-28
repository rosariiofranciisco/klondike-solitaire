from klondike.card import Card, Rank, Suit
from klondike.tableau import TableauPile


def test_new_tableau_is_empty():
    tableau = TableauPile()

    assert tableau.is_empty()
    assert len(tableau) == 0


def test_tableau_inherits_from_pile():
    tableau = TableauPile()

    assert isinstance(tableau, TableauPile)


def test_reveal_top_turns_face_down_card_face_up():
    tableau = TableauPile()
    card = Card(Suit.HEARTS, Rank.ACE)

    tableau.add(card)
    tableau.reveal_top()

    assert card.face_up is True


def test_reveal_top_does_not_change_face_up_card():
    tableau = TableauPile()
    card = Card(Suit.SPADES, Rank.KING, True)

    tableau.add(card)
    tableau.reveal_top()

    assert card.face_up is True


def test_reveal_top_reveals_only_top_card():
    tableau = TableauPile()
    hidden_card = Card(Suit.HEARTS, Rank.ACE)
    top_card = Card(Suit.SPADES, Rank.KING)

    tableau.add(hidden_card)
    tableau.add(top_card)

    tableau.reveal_top()

    assert hidden_card.face_up is False
    assert top_card.face_up is True


def test_reveal_top_on_empty_tableau_does_nothing():
    tableau = TableauPile()

    tableau.reveal_top()

    assert tableau.is_empty()