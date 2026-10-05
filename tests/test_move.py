from klondike.move import Move, MoveType


def test_all_move_types_exist():
    assert len(MoveType) == 6


def test_move_can_be_created_with_only_type():
    move = Move(MoveType.STOCK_TO_WASTE)

    assert move.move_type == MoveType.STOCK_TO_WASTE
    assert move.source_index is None
    assert move.card_index is None
    assert move.target_index is None


def test_move_can_store_indices():
    move = Move(
        MoveType.TABLEAU_TO_TABLEAU,
        source_index=2,
        card_index=4,
        target_index=5,
    )

    assert move.move_type == MoveType.TABLEAU_TO_TABLEAU
    assert move.source_index == 2
    assert move.card_index == 4
    assert move.target_index == 5