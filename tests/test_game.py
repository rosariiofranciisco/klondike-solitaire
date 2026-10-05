from klondike.card import Card, Rank, Suit
from klondike.foundation import FoundationPile
from klondike.game import KlondikeGame
from klondike.move import Move, MoveType
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

def test_move_waste_to_foundation_accepts_ace():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    game.waste.add(ace)

    result = game.move_waste_to_foundation(0)

    assert result is True
    assert len(game.waste) == 0
    assert len(game.foundations[0]) == 1
    assert game.foundations[0].peek() == ace

def test_move_waste_to_foundation_rejects_non_ace_on_empty_foundation():
    game = KlondikeGame()

    card = Card(Suit.HEARTS, Rank.TWO)
    card.face_up = True
    game.waste.add(card)

    result = game.move_waste_to_foundation(0)

    assert result is False
    assert len(game.waste) == 1
    assert game.foundations[0].is_empty()

def test_move_waste_to_foundation_accepts_next_card_of_same_suit():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    two = Card(Suit.HEARTS, Rank.TWO, True)

    game.foundations[0].add(ace)
    game.waste.add(two)

    result = game.move_waste_to_foundation(0)

    assert result is True
    assert game.foundations[0].peek() == two
    assert game.waste.is_empty()


def test_move_waste_to_foundation_rejects_wrong_suit():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    two = Card(Suit.SPADES, Rank.TWO, True)

    game.foundations[0].add(ace)
    game.waste.add(two)

    result = game.move_waste_to_foundation(0)

    assert result is False
    assert game.foundations[0].peek() == ace
    assert game.waste.peek() == two


def test_move_waste_to_foundation_rejects_wrong_rank():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    three = Card(Suit.HEARTS, Rank.THREE, True)

    game.foundations[0].add(ace)
    game.waste.add(three)

    result = game.move_waste_to_foundation(0)

    assert result is False
    assert game.foundations[0].peek() == ace
    assert game.waste.peek() == three

def test_move_tableau_to_foundation_accepts_ace():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    game.tableau[0].add(ace)

    result = game.move_tableau_to_foundation(0, 0)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.foundations[0].peek() == ace


def test_move_tableau_to_foundation_reveals_new_top_card():
    game = KlondikeGame()

    hidden_card = Card(Suit.SPADES, Rank.KING)
    ace = Card(Suit.HEARTS, Rank.ACE, True)

    game.tableau[0].add(hidden_card)
    game.tableau[0].add(ace)

    result = game.move_tableau_to_foundation(0, 0)

    assert result is True
    assert game.foundations[0].peek() == ace
    assert game.tableau[0].peek() == hidden_card
    assert hidden_card.face_up is True


def test_move_tableau_to_foundation_rejects_non_ace_on_empty_foundation():
    game = KlondikeGame()

    two = Card(Suit.HEARTS, Rank.TWO, True)
    game.tableau[0].add(two)

    result = game.move_tableau_to_foundation(0, 0)

    assert result is False
    assert game.tableau[0].peek() == two
    assert game.foundations[0].is_empty()


def test_move_tableau_to_foundation_accepts_next_card_of_same_suit():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    two = Card(Suit.HEARTS, Rank.TWO, True)

    game.foundations[0].add(ace)
    game.tableau[0].add(two)

    result = game.move_tableau_to_foundation(0, 0)

    assert result is True
    assert game.foundations[0].peek() == two
    assert game.tableau[0].is_empty()


def test_move_tableau_to_foundation_rejects_wrong_suit():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    two = Card(Suit.SPADES, Rank.TWO, True)

    game.foundations[0].add(ace)
    game.tableau[0].add(two)

    result = game.move_tableau_to_foundation(0, 0)

    assert result is False
    assert game.foundations[0].peek() == ace
    assert game.tableau[0].peek() == two


def test_move_tableau_to_foundation_rejects_wrong_rank():
    game = KlondikeGame()

    ace = Card(Suit.HEARTS, Rank.ACE, True)
    three = Card(Suit.HEARTS, Rank.THREE, True)

    game.foundations[0].add(ace)
    game.tableau[0].add(three)

    result = game.move_tableau_to_foundation(0, 0)

    assert result is False
    assert game.foundations[0].peek() == ace
    assert game.tableau[0].peek() == three

def test_move_tableau_to_tableau_moves_single_card():
    game = KlondikeGame()

    nine_hearts = Card(Suit.HEARTS, Rank.NINE, True)
    ten_clubs = Card(Suit.CLUBS, Rank.TEN, True)

    game.tableau[0].add(nine_hearts)
    game.tableau[1].add(ten_clubs)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.tableau[1].peek() == nine_hearts

def test_move_tableau_to_tableau_moves_sequence():
    game = KlondikeGame()

    queen_spades = Card(Suit.SPADES, Rank.QUEEN, True)
    jack_hearts = Card(Suit.HEARTS, Rank.JACK, True)
    ten_clubs = Card(Suit.CLUBS, Rank.TEN, True)
    king_diamonds = Card(Suit.DIAMONDS, Rank.KING, True)

    game.tableau[0].add(queen_spades)
    game.tableau[0].add(jack_hearts)
    game.tableau[0].add(ten_clubs)
    game.tableau[1].add(king_diamonds)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.tableau[1].cards == [
        king_diamonds,
        queen_spades,
        jack_hearts,
        ten_clubs,
    ]

def test_move_tableau_to_tableau_reveals_new_top_card():
    game = KlondikeGame()

    hidden_card = Card(Suit.SPADES, Rank.KING)
    queen_hearts = Card(Suit.HEARTS, Rank.QUEEN, True)
    jack_clubs = Card(Suit.CLUBS, Rank.JACK, True)
    king_spades = Card(Suit.SPADES, Rank.KING, True)

    game.tableau[0].add(hidden_card)
    game.tableau[0].add(queen_hearts)
    game.tableau[0].add(jack_clubs)
    game.tableau[1].add(king_spades)

    result = game.move_tableau_to_tableau(0, 1, 1)

    assert result is True
    assert game.tableau[0].peek() == hidden_card
    assert hidden_card.face_up is True

def test_move_tableau_to_tableau_rejects_same_color():
    game = KlondikeGame()

    nine_hearts = Card(Suit.HEARTS, Rank.NINE, True)
    ten_diamonds = Card(Suit.DIAMONDS, Rank.TEN, True)

    game.tableau[0].add(nine_hearts)
    game.tableau[1].add(ten_diamonds)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is False
    assert game.tableau[0].peek() == nine_hearts
    assert game.tableau[1].peek() == ten_diamonds


def test_move_tableau_to_tableau_rejects_wrong_rank():
    game = KlondikeGame()

    eight_hearts = Card(Suit.HEARTS, Rank.EIGHT, True)
    ten_clubs = Card(Suit.CLUBS, Rank.TEN, True)

    game.tableau[0].add(eight_hearts)
    game.tableau[1].add(ten_clubs)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is False
    assert game.tableau[0].peek() == eight_hearts
    assert game.tableau[1].peek() == ten_clubs


def test_move_tableau_to_empty_tableau_accepts_king():
    game = KlondikeGame()

    king_hearts = Card(Suit.HEARTS, Rank.KING, True)

    game.tableau[0].add(king_hearts)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.tableau[1].peek() == king_hearts


def test_move_tableau_to_empty_tableau_rejects_non_king():
    game = KlondikeGame()

    queen_hearts = Card(Suit.HEARTS, Rank.QUEEN, True)

    game.tableau[0].add(queen_hearts)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is False
    assert game.tableau[0].peek() == queen_hearts
    assert game.tableau[1].is_empty()

def test_move_waste_to_tableau_moves_card():
    game = KlondikeGame()

    ten_clubs = Card(Suit.CLUBS, Rank.TEN, True)
    nine_hearts = Card(Suit.HEARTS, Rank.NINE, True)

    game.tableau[0].add(ten_clubs)
    game.waste.add(nine_hearts)

    result = game.move_waste_to_tableau(0)

    assert result is True
    assert game.waste.is_empty()
    assert game.tableau[0].peek() == nine_hearts

def test_move_waste_to_empty_tableau_accepts_king():
    game = KlondikeGame()

    king_hearts = Card(Suit.HEARTS, Rank.KING, True)
    game.waste.add(king_hearts)

    result = game.move_waste_to_tableau(0)

    assert result is True
    assert game.waste.is_empty()
    assert game.tableau[0].peek() == king_hearts

def test_move_waste_to_empty_tableau_rejects_non_king():
    game = KlondikeGame()

    queen_hearts = Card(Suit.HEARTS, Rank.QUEEN, True)
    game.waste.add(queen_hearts)

    result = game.move_waste_to_tableau(0)

    assert result is False
    assert game.waste.peek() == queen_hearts
    assert game.tableau[0].is_empty()

def test_move_waste_to_tableau_rejects_same_color():
    game = KlondikeGame()

    ten_hearts = Card(Suit.HEARTS, Rank.TEN, True)
    nine_diamonds = Card(Suit.DIAMONDS, Rank.NINE, True)

    game.tableau[0].add(ten_hearts)
    game.waste.add(nine_diamonds)

    result = game.move_waste_to_tableau(0)

    assert result is False
    assert game.tableau[0].peek() == ten_hearts
    assert game.waste.peek() == nine_diamonds


def test_move_waste_to_tableau_rejects_wrong_rank():
    game = KlondikeGame()

    ten_clubs = Card(Suit.CLUBS, Rank.TEN, True)
    eight_hearts = Card(Suit.HEARTS, Rank.EIGHT, True)

    game.tableau[0].add(ten_clubs)
    game.waste.add(eight_hearts)

    result = game.move_waste_to_tableau(0)

    assert result is False
    assert game.tableau[0].peek() == ten_clubs
    assert game.waste.peek() == eight_hearts

def test_move_waste_to_tableau_rejects_invalid_index():
    game = KlondikeGame()

    king_hearts = Card(Suit.HEARTS, Rank.KING, True)
    game.waste.add(king_hearts)

    assert game.move_waste_to_tableau(-1) is False
    assert game.move_waste_to_tableau(7) is False

    assert game.waste.peek() == king_hearts

def test_move_foundation_to_tableau_moves_valid_card():
    game = KlondikeGame()

    card = Card(Suit.HEARTS, Rank.QUEEN, True)
    foundation_card = Card(Suit.CLUBS, Rank.JACK, True)

    game.foundations[0].add(foundation_card)
    game.tableau[0].add(card)

    result = game.move_foundation_to_tableau(0, 0)

    assert result is True
    assert game.foundations[0].is_empty()
    assert game.tableau[0].peek() == foundation_card


def test_move_foundation_to_empty_tableau_accepts_king():
    game = KlondikeGame()

    card = Card(Suit.SPADES, Rank.KING, True)
    game.foundations[0].add(card)

    result = game.move_foundation_to_tableau(0, 0)

    assert result is True
    assert game.foundations[0].is_empty()
    assert game.tableau[0].peek() == card


def test_move_foundation_to_empty_tableau_rejects_non_king():
    game = KlondikeGame()

    card = Card(Suit.SPADES, Rank.QUEEN, True)
    game.foundations[0].add(card)

    result = game.move_foundation_to_tableau(0, 0)

    assert result is False
    assert game.foundations[0].peek() == card
    assert game.tableau[0].is_empty()


def test_move_foundation_to_tableau_rejects_same_color():
    game = KlondikeGame()

    foundation_card = Card(Suit.HEARTS, Rank.QUEEN, True)
    tableau_card = Card(Suit.DIAMONDS, Rank.KING, True)

    game.foundations[0].add(foundation_card)
    game.tableau[0].add(tableau_card)

    result = game.move_foundation_to_tableau(0, 0)

    assert result is False
    assert game.foundations[0].peek() == foundation_card
    assert game.tableau[0].peek() == tableau_card


def test_move_foundation_to_tableau_rejects_wrong_rank():
    game = KlondikeGame()

    foundation_card = Card(Suit.HEARTS, Rank.QUEEN, True)
    tableau_card = Card(Suit.CLUBS, Rank.JACK, True)

    game.foundations[0].add(foundation_card)
    game.tableau[0].add(tableau_card)

    result = game.move_foundation_to_tableau(0, 0)

    assert result is False
    assert game.foundations[0].peek() == foundation_card
    assert game.tableau[0].peek() == tableau_card


def test_move_foundation_to_tableau_rejects_empty_foundation():
    game = KlondikeGame()

    result = game.move_foundation_to_tableau(0, 0)

    assert result is False
    assert game.tableau[0].is_empty()


def test_move_foundation_to_tableau_rejects_invalid_foundation_index():
    game = KlondikeGame()

    result = game.move_foundation_to_tableau(4, 0)

    assert result is False


def test_move_foundation_to_tableau_rejects_invalid_tableau_index():
    game = KlondikeGame()

    result = game.move_foundation_to_tableau(0, 7)

    assert result is False

def test_recycle_waste_to_stock_moves_all_cards():
    game = KlondikeGame()

    first_card = Card(Suit.HEARTS, Rank.ACE, True)
    second_card = Card(Suit.CLUBS, Rank.TWO, True)
    third_card = Card(Suit.SPADES, Rank.THREE, True)

    game.waste.add(first_card)
    game.waste.add(second_card)
    game.waste.add(third_card)

    game.recycle_waste_to_stock()

    assert game.waste.is_empty()
    assert len(game.stock) == 3
    assert game.stock.peek() == first_card

def test_recycle_waste_to_stock_turns_cards_face_down():
    game = KlondikeGame()

    first_card = Card(Suit.HEARTS, Rank.ACE, True)
    second_card = Card(Suit.CLUBS, Rank.TWO, True)

    game.waste.add(first_card)
    game.waste.add(second_card)

    game.recycle_waste_to_stock()

    assert all(not card.face_up for card in game.stock.cards)

def test_recycle_empty_waste_does_nothing():
    game = KlondikeGame()

    game.recycle_waste_to_stock()

    assert game.waste.is_empty()
    assert game.stock.is_empty()

def test_is_won_returns_false_for_new_game():
    game = KlondikeGame()

    assert game.is_won() is False


def test_is_won_returns_false_when_foundations_are_not_complete():
    game = KlondikeGame()

    for foundation in game.foundations:
        for rank in range(1, 13):
            foundation.add(Card(Suit.HEARTS, Rank(rank), True))

    assert game.is_won() is False


def test_is_won_returns_true_when_all_52_cards_are_in_foundations():
    game = KlondikeGame()

    for foundation, suit in zip(
        game.foundations,
        Suit,
        strict=False,
    ):
        for rank in Rank:
            foundation.add(Card(suit, rank, True))

    assert game.is_won() is True

def test_can_move_waste_to_foundation_returns_true_for_valid_move():
    game = KlondikeGame()

    foundation_card = Card(Suit.HEARTS, Rank.FOUR, True)
    waste_card = Card(Suit.HEARTS, Rank.FIVE, True)

    game.foundations[0].add(foundation_card)
    game.waste.add(waste_card)

    assert game.can_move_waste_to_foundation(0) is True


def test_can_move_waste_to_foundation_does_not_change_game():
    game = KlondikeGame()

    foundation_card = Card(Suit.HEARTS, Rank.FOUR, True)
    waste_card = Card(Suit.HEARTS, Rank.FIVE, True)

    game.foundations[0].add(foundation_card)
    game.waste.add(waste_card)

    result = game.can_move_waste_to_foundation(0)

    assert result is True
    assert game.foundations[0].peek() == foundation_card
    assert game.waste.peek() == waste_card


def test_can_move_waste_to_foundation_rejects_invalid_move():
    game = KlondikeGame()

    foundation_card = Card(Suit.HEARTS, Rank.FOUR, True)
    waste_card = Card(Suit.CLUBS, Rank.SIX, True)

    game.foundations[0].add(foundation_card)
    game.waste.add(waste_card)

    assert game.can_move_waste_to_foundation(0) is False

def test_can_move_waste_to_tableau_returns_true_for_valid_move():
    game = KlondikeGame()

    tableau_card = Card(Suit.HEARTS, Rank.QUEEN, True)
    waste_card = Card(Suit.CLUBS, Rank.JACK, True)

    game.tableau[0].add(tableau_card)
    game.waste.add(waste_card)

    assert game.can_move_waste_to_tableau(0) is True


def test_can_move_waste_to_tableau_does_not_change_game():
    game = KlondikeGame()

    tableau_card = Card(Suit.HEARTS, Rank.QUEEN, True)
    waste_card = Card(Suit.CLUBS, Rank.JACK, True)

    game.tableau[0].add(tableau_card)
    game.waste.add(waste_card)

    result = game.can_move_waste_to_tableau(0)

    assert result is True
    assert game.tableau[0].peek() == tableau_card
    assert game.waste.peek() == waste_card


def test_can_move_waste_to_tableau_rejects_invalid_move():
    game = KlondikeGame()

    tableau_card = Card(Suit.HEARTS, Rank.QUEEN, True)
    waste_card = Card(Suit.DIAMONDS, Rank.JACK, True)

    game.tableau[0].add(tableau_card)
    game.waste.add(waste_card)

    assert game.can_move_waste_to_tableau(0) is False

def test_can_move_tableau_to_foundation_returns_true_for_valid_move():
    game = KlondikeGame()

    tableau_card = Card(Suit.HEARTS, Rank.FIVE, True)
    foundation_card = Card(Suit.HEARTS, Rank.FOUR, True)

    game.tableau[0].add(tableau_card)
    game.foundations[0].add(foundation_card)

    assert game.can_move_tableau_to_foundation(0, 0) is True


def test_can_move_tableau_to_foundation_does_not_change_game():
    game = KlondikeGame()

    tableau_card = Card(Suit.HEARTS, Rank.FIVE, True)
    foundation_card = Card(Suit.HEARTS, Rank.FOUR, True)

    game.tableau[0].add(tableau_card)
    game.foundations[0].add(foundation_card)

    result = game.can_move_tableau_to_foundation(0, 0)

    assert result is True
    assert game.tableau[0].peek() == tableau_card
    assert game.foundations[0].peek() == foundation_card


def test_can_move_tableau_to_foundation_accepts_ace_on_empty_foundation():
    game = KlondikeGame()

    ace = Card(Suit.SPADES, Rank.ACE, True)
    game.tableau[0].add(ace)

    assert game.can_move_tableau_to_foundation(0, 0) is True


def test_can_move_tableau_to_foundation_rejects_invalid_move():
    game = KlondikeGame()

    tableau_card = Card(Suit.HEARTS, Rank.FIVE, True)
    foundation_card = Card(Suit.CLUBS, Rank.FOUR, True)

    game.tableau[0].add(tableau_card)
    game.foundations[0].add(foundation_card)

    assert game.can_move_tableau_to_foundation(0, 0) is False

def test_can_move_foundation_to_tableau_returns_true_for_valid_move():
    game = KlondikeGame()

    foundation_card = Card(Suit.CLUBS, Rank.JACK, True)
    tableau_card = Card(Suit.HEARTS, Rank.QUEEN, True)

    game.foundations[0].add(foundation_card)
    game.tableau[0].add(tableau_card)

    assert game.can_move_foundation_to_tableau(0, 0) is True


def test_can_move_foundation_to_tableau_does_not_change_game():
    game = KlondikeGame()

    foundation_card = Card(Suit.CLUBS, Rank.JACK, True)
    tableau_card = Card(Suit.HEARTS, Rank.QUEEN, True)

    game.foundations[0].add(foundation_card)
    game.tableau[0].add(tableau_card)

    result = game.can_move_foundation_to_tableau(0, 0)

    assert result is True
    assert game.foundations[0].peek() == foundation_card
    assert game.tableau[0].peek() == tableau_card


def test_can_move_foundation_to_empty_tableau_accepts_king():
    game = KlondikeGame()

    king = Card(Suit.SPADES, Rank.KING, True)
    game.foundations[0].add(king)

    assert game.can_move_foundation_to_tableau(0, 0) is True


def test_can_move_foundation_to_empty_tableau_rejects_non_king():
    game = KlondikeGame()

    card = Card(Suit.SPADES, Rank.QUEEN, True)
    game.foundations[0].add(card)

    assert game.can_move_foundation_to_tableau(0, 0) is False


def test_can_move_foundation_to_tableau_rejects_invalid_move():
    game = KlondikeGame()

    foundation_card = Card(Suit.HEARTS, Rank.JACK, True)
    tableau_card = Card(Suit.DIAMONDS, Rank.QUEEN, True)

    game.foundations[0].add(foundation_card)
    game.tableau[0].add(tableau_card)

    assert game.can_move_foundation_to_tableau(0, 0) is False


def test_can_move_foundation_to_tableau_rejects_empty_foundation():
    game = KlondikeGame()

    assert game.can_move_foundation_to_tableau(0, 0) is False

def test_can_move_tableau_to_tableau_returns_true_for_valid_sequence():
    game = KlondikeGame()

    source = game.tableau[0]
    target = game.tableau[1]

    source.add(Card(Suit.HEARTS, Rank.NINE, True))
    source.add(Card(Suit.CLUBS, Rank.EIGHT, True))
    source.add(Card(Suit.HEARTS, Rank.SEVEN, True))

    target.add(Card(Suit.CLUBS, Rank.TEN, True))

    assert game.can_move_tableau_to_tableau(0, 0, 1) is True


def test_can_move_tableau_to_tableau_does_not_change_game():
    game = KlondikeGame()

    source = game.tableau[0]
    target = game.tableau[1]

    first_card = Card(Suit.HEARTS, Rank.NINE, True)
    second_card = Card(Suit.CLUBS, Rank.EIGHT, True)
    target_card = Card(Suit.CLUBS, Rank.TEN, True)

    source.add(first_card)
    source.add(second_card)
    target.add(target_card)

    result = game.can_move_tableau_to_tableau(0, 0, 1)

    assert result is True
    assert source.cards == [first_card, second_card]
    assert target.peek() == target_card


def test_can_move_tableau_to_empty_tableau_requires_king():
    game = KlondikeGame()

    game.tableau[0].add(Card(Suit.SPADES, Rank.KING, True))

    assert game.can_move_tableau_to_tableau(0, 0, 1) is True


def test_can_move_tableau_to_empty_tableau_rejects_non_king():
    game = KlondikeGame()

    game.tableau[0].add(Card(Suit.SPADES, Rank.QUEEN, True))

    assert game.can_move_tableau_to_tableau(0, 0, 1) is False


def test_can_move_tableau_to_tableau_rejects_invalid_sequence():
    game = KlondikeGame()

    game.tableau[0].add(Card(Suit.HEARTS, Rank.NINE, True))
    game.tableau[0].add(Card(Suit.DIAMONDS, Rank.EIGHT, True))

    game.tableau[1].add(Card(Suit.CLUBS, Rank.TEN, True))

    assert game.can_move_tableau_to_tableau(0, 0, 1) is False


def test_can_move_tableau_to_tableau_rejects_invalid_target():
    game = KlondikeGame()

    game.tableau[0].add(Card(Suit.HEARTS, Rank.NINE, True))
    game.tableau[1].add(Card(Suit.DIAMONDS, Rank.TEN, True))

    assert game.can_move_tableau_to_tableau(0, 0, 1) is False

def test_game_is_not_over_when_stock_has_cards():
    game = KlondikeGame()

    game.stock.add(Card(Suit.HEARTS, Rank.ACE))

    assert game.is_game_over() is False


def test_game_is_not_over_when_waste_has_cards():
    game = KlondikeGame()

    game.waste.add(Card(Suit.HEARTS, Rank.ACE, True))

    assert game.is_game_over() is False


def test_game_is_over_when_won():
    game = KlondikeGame()

    for suit in Suit:
        foundation = game.foundations[list(Suit).index(suit)]

        for rank in Rank:
            foundation.add(Card(suit, rank, True))

    assert game.is_game_over() is True


def test_empty_game_is_game_over():
    game = KlondikeGame()

    assert game.is_game_over() is True

def test_execute_stock_to_waste():
    game = KlondikeGame()

    card = Card(Suit.HEARTS, Rank.ACE)
    game.stock.add(card)

    result = game.execute_move(
        Move(MoveType.STOCK_TO_WASTE)
    )

    assert result is True
    assert len(game.stock) == 0
    assert len(game.waste) == 1
    assert game.waste.peek() == card
    assert card.face_up is True


def test_execute_waste_to_foundation():
    game = KlondikeGame()

    card = Card(Suit.HEARTS, Rank.ACE, True)
    game.waste.add(card)

    result = game.execute_move(
        Move(
            MoveType.WASTE_TO_FOUNDATION,
            target_index=0,
        )
    )

    assert result is True
    assert len(game.waste) == 0
    assert game.foundations[0].peek() == card


def test_execute_waste_to_tableau():
    game = KlondikeGame()

    card = Card(Suit.SPADES, Rank.KING, True)
    game.waste.add(card)

    result = game.execute_move(
        Move(
            MoveType.WASTE_TO_TABLEAU,
            target_index=0,
        )
    )

    assert result is True
    assert len(game.waste) == 0
    assert game.tableau[0].peek() == card


def test_execute_tableau_to_foundation():
    game = KlondikeGame()

    card = Card(Suit.HEARTS, Rank.ACE, True)
    game.tableau[0].add(card)

    result = game.execute_move(
        Move(
            MoveType.TABLEAU_TO_FOUNDATION,
            source_index=0,
            target_index=0,
        )
    )

    assert result is True
    assert len(game.tableau[0]) == 0
    assert game.foundations[0].peek() == card


def test_execute_tableau_to_tableau():
    game = KlondikeGame()

    moving_card = Card(Suit.HEARTS, Rank.NINE, True)
    target_card = Card(Suit.CLUBS, Rank.TEN, True)

    game.tableau[0].add(moving_card)
    game.tableau[1].add(target_card)

    result = game.execute_move(
        Move(
            MoveType.TABLEAU_TO_TABLEAU,
            source_index=0,
            card_index=0,
            target_index=1,
        )
    )

    assert result is True
    assert len(game.tableau[0]) == 0
    assert game.tableau[1].peek() == moving_card


def test_execute_foundation_to_tableau():
    game = KlondikeGame()

    foundation_card = Card(Suit.HEARTS, Rank.KING, True)
    game.foundations[0].add(foundation_card)

    result = game.execute_move(
        Move(
            MoveType.FOUNDATION_TO_TABLEAU,
            source_index=0,
            target_index=0,
        )
    )

    assert result is True
    assert len(game.foundations[0]) == 0
    assert game.tableau[0].peek() == foundation_card

def test_execute_stock_to_waste_returns_false_when_stock_is_empty():
    game = KlondikeGame()

    result = game.execute_move(
        Move(MoveType.STOCK_TO_WASTE)
    )

    assert result is False

def test_draw_from_stock_returns_false_when_stock_is_empty():
    game = KlondikeGame()

    assert game.draw_from_stock() is False