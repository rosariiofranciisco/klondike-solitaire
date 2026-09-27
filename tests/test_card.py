from klondike.card import Card, Rank, Suit


def test_card_has_correct_attributes():
    card = Card(Suit.HEARTS, Rank.ACE)

    assert card.suit == Suit.HEARTS
    assert card.rank == Rank.ACE
    assert card.face_up is False


def test_card_can_be_face_up():
    card = Card(Suit.SPADES, Rank.KING, True)

    assert card.suit == Suit.SPADES
    assert card.rank == Rank.KING
    assert card.face_up is True


def test_ranks_have_correct_order():
    assert Rank.ACE < Rank.TWO
    assert Rank.QUEEN < Rank.KING


def test_all_suits_exist():
    assert len(Suit) == 4


def test_all_ranks_exist():
    assert len(Rank) == 13