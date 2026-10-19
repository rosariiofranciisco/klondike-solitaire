"""Pygame graphical interface for Klondike Solitaire."""

import pygame

from klondike.game import KlondikeGame
from klondike.move import Move, MoveType

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650

CARD_WIDTH = 70
CARD_HEIGHT = 100

MARGIN_X = 40
TOP_ROW_Y = 40
TABLEAU_Y = 220

COLUMN_GAP = 35
CARD_SLOT_GAP = 20
TABLEAU_CARD_OFFSET = 25

BACKGROUND_COLOR = (30, 120, 70)
CARD_COLOR = (250, 250, 250)
CARD_BORDER_COLOR = (40, 40, 40)
CARD_BACK_COLOR = (35, 65, 125)
CARD_BACK_BORDER_COLOR = (230, 230, 230)
CARD_BACK_INNER_COLOR = (100, 140, 200)
EMPTY_SLOT_COLOR = (230, 230, 230)
RED_CARD_COLOR = (200, 30, 45)
BLACK_CARD_COLOR = (25, 25, 25)

RANK_LABELS = {
    1: "A",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "J",
    12: "Q",
    13: "K",
}

class KlondikeGUI:
    """Represent the graphical interface of the Klondike game."""

    def __init__(self) -> None:
        pygame.init()

        self.rank_font = pygame.font.SysFont("arial", 18, bold=True)
        self.suit_font = pygame.font.SysFont("segoe ui symbol", 22)

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        pygame.display.set_caption("Klondike Solitaire")

        self.clock = pygame.time.Clock()
        self.game = KlondikeGame()
        self.game.start_new_game()

        self.running = True

        self.selected_source: tuple[MoveType, int, int | None] | None = None

    def run(self) -> None:
        """Run the main graphical loop."""
        while self.running:
            self._handle_events()
            self._draw()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_left_click(event.pos)


    def _handle_left_click(self, position: tuple[int, int]) -> None:
        """Handle a left mouse button click."""
        x, y = position

        stock_x = MARGIN_X
        stock_y = TOP_ROW_Y
        waste_x = MARGIN_X + CARD_WIDTH + CARD_SLOT_GAP


        if (
            stock_x <= x <= stock_x + CARD_WIDTH
            and stock_y <= y <= stock_y + CARD_HEIGHT
        ):
            if self.game.stock.is_empty():
                self.game.execute_move(
                    Move(MoveType.RECYCLE_WASTE_TO_STOCK)
                )
            else:
                self.game.execute_move(
                    Move(MoveType.STOCK_TO_WASTE)
                )

            self.selected_source = None
            return


        if (
            waste_x <= x <= waste_x + CARD_WIDTH
            and stock_y <= y <= stock_y + CARD_HEIGHT
        ):
            if not self.game.waste.is_empty():
                self.selected_source = (
                    MoveType.WASTE_TO_TABLEAU,
                    0,
                    None,
                )
            return


        foundation_start_x = (
            WINDOW_WIDTH
            - MARGIN_X
            - (4 * CARD_WIDTH + 3 * CARD_SLOT_GAP)
        )

        if TOP_ROW_Y <= y <= TOP_ROW_Y + CARD_HEIGHT:
            for index in range(len(self.game.foundations)):
                foundation_x = foundation_start_x + index * (
                    CARD_WIDTH + CARD_SLOT_GAP
                )

                if foundation_x <= x <= foundation_x + CARD_WIDTH:
                    if self.selected_source is not None:
                        source_type, source_index, card_index = (
                            self.selected_source
                        )

                        if source_type == MoveType.WASTE_TO_TABLEAU:
                            self.game.execute_move(
                                Move(
                                    move_type=MoveType.WASTE_TO_FOUNDATION,
                                    target_index=index,
                                )
                            )

                        elif source_type == MoveType.TABLEAU_TO_TABLEAU:
                            self.game.execute_move(
                                Move(
                                    move_type=MoveType.TABLEAU_TO_FOUNDATION,
                                    source_index=source_index,
                                    card_index=card_index,
                                    target_index=index,
                                )
                            )

                    elif not self.game.waste.is_empty():
                        self.game.execute_move(
                            Move(
                                move_type=MoveType.WASTE_TO_FOUNDATION,
                                target_index=index,
                            )
                        )

                    self.selected_source = None
                    return

        if y < TABLEAU_Y:
            return

        column_width = CARD_WIDTH + COLUMN_GAP
        column = (x - MARGIN_X) // column_width

        if not 0 <= column < len(self.game.tableau):
            return

        if self.selected_source is None:
            pile = self.game.tableau[column]

            if pile.is_empty():
                return

            for card_index in range(len(pile.cards) - 1, -1, -1):
                card_y = TABLEAU_Y + card_index * TABLEAU_CARD_OFFSET

                if card_y <= y <= card_y + CARD_HEIGHT:
                    if pile.cards[card_index].face_up:
                        self.selected_source = (
                            MoveType.TABLEAU_TO_TABLEAU,
                            column,
                            card_index,
                        )
                        return

            return

        source_type, source_index, card_index = self.selected_source

        if source_type == MoveType.WASTE_TO_TABLEAU:
            self.game.execute_move(
                Move(
                    move_type=MoveType.WASTE_TO_TABLEAU,
                    source_index=source_index,
                    target_index=column,
                )
            )

        elif source_type == MoveType.TABLEAU_TO_TABLEAU:
            if source_index != column:
                self.game.execute_move(
                    Move(
                        move_type=MoveType.TABLEAU_TO_TABLEAU,
                        source_index=source_index,
                        card_index=card_index,
                        target_index=column,
                    )
                )

        self.selected_source = None


    def _draw(self) -> None:
        """Draw the current game state."""
        self.screen.fill(BACKGROUND_COLOR)

        self._draw_top_row()
        self._draw_tableau()

    def _draw_card_back(self, x: int, y: int) -> None:
        """Draw a face-down card."""
        pygame.draw.rect(
            self.screen,
            (35, 65, 125),
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            border_radius=5,
        )

        pygame.draw.rect(
            self.screen,
            (230, 230, 230),
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            width=2,
            border_radius=5,
        )

        pygame.draw.rect(
            self.screen,
            (100, 140, 200),
            (x + 6, y + 6, CARD_WIDTH - 12, CARD_HEIGHT - 12),
            width=2,
            border_radius=3,
        )

    def _draw_card(self, card, x: int, y: int) -> None:
        """Draw a face-up card."""
        pygame.draw.rect(
            self.screen,
            CARD_COLOR,
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            border_radius=5,
        )

        pygame.draw.rect(
            self.screen,
            CARD_BORDER_COLOR,
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            width=2,
            border_radius=5,
        )

        red_suits = {"♥", "♦"}
        color = (
            RED_CARD_COLOR
            if card.suit.value in red_suits
            else BLACK_CARD_COLOR
        )

        rank_text = self.rank_font.render(
            RANK_LABELS[int(card.rank)],
            True,
            color,
        )
        suit_text = self.suit_font.render(
            card.suit.value,
            True,
            color,
        )

        self.screen.blit(rank_text, (x + 6, y + 5))
        self.screen.blit(suit_text, (x + 6, y + 27))

    def _draw_top_row(self) -> None:
        """Draw the stock, waste, and foundation piles."""
        stock_x = MARGIN_X
        waste_x = MARGIN_X + CARD_WIDTH + CARD_SLOT_GAP

        if self.game.stock.is_empty():
            pygame.draw.rect(
                self.screen,
                (230, 230, 230),
                (stock_x, TOP_ROW_Y, CARD_WIDTH, CARD_HEIGHT),
                width=2,
                border_radius=5,
            )
        else:
            self._draw_card_back(stock_x, TOP_ROW_Y)

        if not self.game.waste.is_empty():
            self._draw_card(
                self.game.waste.peek(),
                waste_x,
                TOP_ROW_Y,
            )
        else:
            pygame.draw.rect(
                self.screen,
                (230, 230, 230),
                (waste_x, TOP_ROW_Y, CARD_WIDTH, CARD_HEIGHT),
                width=2,
                border_radius=5,
            )

        if (
            self.selected_source is not None
            and self.selected_source[0] == MoveType.WASTE_TO_TABLEAU
        ):
            self._draw_selection(waste_x, TOP_ROW_Y)

        foundation_start_x = (
            WINDOW_WIDTH - MARGIN_X - (4 * CARD_WIDTH + 3 * 20)
        )

        for foundation_index, foundation in enumerate(
            self.game.foundations
        ):
            x = foundation_start_x + foundation_index * (
                CARD_WIDTH + CARD_SLOT_GAP
            )

            if foundation.is_empty():
                pygame.draw.rect(
                    self.screen,
                    (230, 230, 230),
                    (x, TOP_ROW_Y, CARD_WIDTH, CARD_HEIGHT),
                    width=2,
                    border_radius=5,
                )
            else:
                self._draw_card(
                    foundation.peek(),
                    x,
                    TOP_ROW_Y,
                )

    def _draw_tableau(self) -> None:
        """Draw the seven tableau piles and their cards."""
        for tableau_index, pile in enumerate(self.game.tableau):
            x = MARGIN_X + tableau_index * (
                CARD_WIDTH + COLUMN_GAP
            )

            if pile.is_empty():
                pygame.draw.rect(
                    self.screen,
                    (230, 230, 230),
                    (x, TABLEAU_Y, CARD_WIDTH, CARD_HEIGHT),
                    width=2,
                    border_radius=5,
                )
                continue

            for card_index, card in enumerate(pile.cards):
                y = TABLEAU_Y + card_index * TABLEAU_CARD_OFFSET

                if card.face_up:
                    self._draw_card(card, x, y)
                else:
                    self._draw_card_back(x, y)

                if (
                    self.selected_source is not None
                    and self.selected_source[0] == MoveType.TABLEAU_TO_TABLEAU
                    and self.selected_source[1] == tableau_index
                    and self.selected_source[2] == card_index
                ):
                    self._draw_selection(x, y)


    def _draw_selection(self, x: int, y: int) -> None:
        """Draw a highlight around a selected card."""
        pygame.draw.rect(
            self.screen,
            (255, 215, 0),
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            width=4,
            border_radius=5,
        )


def main() -> None:
    """Start the Klondike graphical interface."""
    gui = KlondikeGUI()
    gui.run()


if __name__ == "__main__":
    main()