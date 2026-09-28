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

def test_can_move_sequence_accepts_valid_sequence():
    tableau = TableauPile()

    nine_hearts = Card(Suit.HEARTS, Rank.NINE, True)
    eight_clubs = Card(Suit.CLUBS, Rank.EIGHT, True)
    seven_hearts = Card(Suit.HEARTS, Rank.SEVEN, True)

    tableau.add(nine_hearts)
    tableau.add(eight_clubs)
    tableau.add(seven_hearts)

    assert tableau.can_move_sequence(0) is True


def test_can_move_sequence_accepts_sequence_starting_in_middle():
    tableau = TableauPile()

    king_spades = Card(Suit.SPADES, Rank.KING, True)
    queen_hearts = Card(Suit.HEARTS, Rank.QUEEN, True)
    jack_clubs = Card(Suit.CLUBS, Rank.JACK, True)

    tableau.add(king_spades)
    tableau.add(queen_hearts)
    tableau.add(jack_clubs)

    assert tableau.can_move_sequence(1) is True


def test_can_move_sequence_rejects_same_color():
    tableau = TableauPile()

    nine_hearts = Card(Suit.HEARTS, Rank.NINE, True)
    eight_diamonds = Card(Suit.DIAMONDS, Rank.EIGHT, True)

    tableau.add(nine_hearts)
    tableau.add(eight_diamonds)

    assert tableau.can_move_sequence(0) is False


def test_can_move_sequence_rejects_wrong_rank():
    tableau = TableauPile()

    nine_hearts = Card(Suit.HEARTS, Rank.NINE, True)
    seven_clubs = Card(Suit.CLUBS, Rank.SEVEN, True)

    tableau.add(nine_hearts)
    tableau.add(seven_clubs)

    assert tableau.can_move_sequence(0) is False


def test_can_move_sequence_rejects_face_down_card():
    tableau = TableauPile()

    nine_hearts = Card(Suit.HEARTS, Rank.NINE)
    eight_clubs = Card(Suit.CLUBS, Rank.EIGHT, True)

    tableau.add(nine_hearts)
    tableau.add(eight_clubs)

    assert tableau.can_move_sequence(0) is False


def test_can_move_sequence_rejects_invalid_index():
    tableau = TableauPile()

    card = Card(Suit.HEARTS, Rank.ACE, True)
    tableau.add(card)

    assert tableau.can_move_sequence(-1) is False
    assert tableau.can_move_sequence(1) is False