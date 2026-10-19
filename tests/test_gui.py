from klondike.gui import (
    CARD_HEIGHT,
    CARD_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


def test_gui_dimensions():
    assert WINDOW_WIDTH == 900
    assert WINDOW_HEIGHT == 650
    assert CARD_WIDTH == 70
    assert CARD_HEIGHT == 100