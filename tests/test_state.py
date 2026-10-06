from klondike.card import Card, Rank, Suit
from klondike.state import GameState


def test_game_state_stores_game_data():
    card = Card(Suit.HEARTS, Rank.ACE, True)

    state = GameState(
        tableau=[[card]],
        foundations=[[], [], [], []],
        stock=[],
        waste=[],
    )

    assert state.tableau == [[card]]
    assert state.foundations == [[], [], [], []]
    assert state.stock == []
    assert state.waste == []
