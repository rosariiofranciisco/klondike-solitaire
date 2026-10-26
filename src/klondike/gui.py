"""Pygame graphical interface for Klondike Solitaire."""

import pygame

from klondike.config import (
    BACKGROUND_COLOR,
    BLACK_CARD_COLOR,
    CARD_BACK_COLOR,
    CARD_BACK_INNER_COLOR,
    CARD_BORDER_COLOR,
    CARD_BORDER_WIDTH,
    CARD_COLOR,
    CARD_CORNER_RADIUS,
    CARD_HEIGHT,
    CARD_INNER_CORNER_RADIUS,
    CARD_INNER_PADDING,
    CARD_RANK_Y_OFFSET,
    CARD_SLOT_GAP,
    CARD_SUIT_Y_OFFSET,
    CARD_TEXT_X_OFFSET,
    CARD_WIDTH,
    COLUMN_GAP,
    EMPTY_SLOT_COLOR,
    FONT_BOLD,
    FONT_NAME,
    FONT_SIZE,
    FOUNDATION_COUNT,
    FPS,
    MARGIN_X,
    RANK_LABELS,
    RED_CARD_COLOR,
    RED_SUITS,
    SELECTION_BORDER_WIDTH,
    SELECTION_COLOR,
    SUIT_FONT_NAME,
    SUIT_FONT_SIZE,
    TABLEAU_CARD_OFFSET,
    TABLEAU_Y,
    TOP_ROW_Y,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from klondike.game import KlondikeGame
from klondike.move import Move, MoveType


class KlondikeGUI:
    """Represent the graphical interface of the Klondike game."""

    def __init__(self) -> None:
        pygame.init()

        self.rank_font = pygame.font.SysFont(
            FONT_NAME,
            FONT_SIZE,
            bold=FONT_BOLD,
        )
        self.suit_font = pygame.font.SysFont(
            SUIT_FONT_NAME,
            SUIT_FONT_SIZE,
        )

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        pygame.display.set_caption(WINDOW_TITLE)

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
            self.clock.tick(FPS)

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
            - (
                FOUNDATION_COUNT * CARD_WIDTH
                + (FOUNDATION_COUNT - 1) * CARD_SLOT_GAP
            )
        )

        if TOP_ROW_Y <= y <= TOP_ROW_Y + CARD_HEIGHT:
            for index, foundation in enumerate(self.game.foundations):
                foundation_x = foundation_start_x + index * (
                    CARD_WIDTH + CARD_SLOT_GAP
                )

                if foundation_x <= x <= foundation_x + CARD_WIDTH:
                    if self.selected_source is None:
                        if not foundation.is_empty():
                            self.selected_source = (
                                MoveType.FOUNDATION_TO_TABLEAU,
                                index,
                                None,
                            )
                    else:
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
                            self.selected_source = None

                        elif source_type == MoveType.TABLEAU_TO_TABLEAU:
                            self.game.execute_move(
                                Move(
                                    move_type=MoveType.TABLEAU_TO_FOUNDATION,
                                    source_index=source_index,
                                    target_index=index,
                                )
                            )
                            self.selected_source = None

                        elif source_type == MoveType.FOUNDATION_TO_TABLEAU:
                            if not foundation.is_empty():
                                self.selected_source = (
                                    MoveType.FOUNDATION_TO_TABLEAU,
                                    index,
                                    None,
                                )
                            else:
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

        if source_type == MoveType.FOUNDATION_TO_TABLEAU:
            self.game.execute_move(
                Move(
                    move_type=MoveType.FOUNDATION_TO_TABLEAU,
                    source_index=source_index,
                    target_index=column,
                )
            )

        elif source_type == MoveType.WASTE_TO_TABLEAU:
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
            CARD_BACK_COLOR,
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            border_radius=CARD_CORNER_RADIUS,
        )

        pygame.draw.rect(
            self.screen,
            EMPTY_SLOT_COLOR,
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            width=CARD_BORDER_WIDTH,
            border_radius=CARD_CORNER_RADIUS,
        )

        pygame.draw.rect(
            self.screen,
            CARD_BACK_INNER_COLOR,
            (
                x + CARD_INNER_PADDING,
                y + CARD_INNER_PADDING,
                CARD_WIDTH - 2 * CARD_INNER_PADDING,
                CARD_HEIGHT - 2 * CARD_INNER_PADDING,
            ),
            width=CARD_BORDER_WIDTH,
            border_radius=CARD_INNER_CORNER_RADIUS,
        )

    def _draw_card(self, card, x: int, y: int) -> None:
        """Draw a face-up card."""
        pygame.draw.rect(
            self.screen,
            CARD_COLOR,
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            border_radius=CARD_CORNER_RADIUS,
        )

        pygame.draw.rect(
            self.screen,
            CARD_BORDER_COLOR,
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            width=CARD_BORDER_WIDTH,
            border_radius=CARD_CORNER_RADIUS,
        )

        color = (
            RED_CARD_COLOR
            if card.suit.value in RED_SUITS
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

        self.screen.blit(
            rank_text,
            (x + CARD_TEXT_X_OFFSET, y + CARD_RANK_Y_OFFSET),
        )
        self.screen.blit(
            suit_text,
            (x + CARD_TEXT_X_OFFSET, y + CARD_SUIT_Y_OFFSET),
        )

    def _draw_top_row(self) -> None:
        """Draw the stock, waste, and foundation piles."""
        stock_x = MARGIN_X
        waste_x = MARGIN_X + CARD_WIDTH + CARD_SLOT_GAP

        if self.game.stock.is_empty():
            pygame.draw.rect(
                self.screen,
                EMPTY_SLOT_COLOR,
                (stock_x, TOP_ROW_Y, CARD_WIDTH, CARD_HEIGHT),
                width=CARD_BORDER_WIDTH,
                border_radius=CARD_CORNER_RADIUS,
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
                EMPTY_SLOT_COLOR,
                (waste_x, TOP_ROW_Y, CARD_WIDTH, CARD_HEIGHT),
                width=CARD_BORDER_WIDTH,
                border_radius=CARD_CORNER_RADIUS,
            )

        if (
            self.selected_source is not None
            and self.selected_source[0] == MoveType.WASTE_TO_TABLEAU
        ):
            self._draw_selection(waste_x, TOP_ROW_Y)

        foundation_start_x = (
            WINDOW_WIDTH
            - MARGIN_X
            - (
                FOUNDATION_COUNT * CARD_WIDTH
                + (FOUNDATION_COUNT - 1) * CARD_SLOT_GAP
            )
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
                    EMPTY_SLOT_COLOR,
                    (x, TOP_ROW_Y, CARD_WIDTH, CARD_HEIGHT),
                    width=CARD_BORDER_WIDTH,
                    border_radius=CARD_CORNER_RADIUS,
                )
            else:
                self._draw_card(
                    foundation.peek(),
                    x,
                    TOP_ROW_Y,
                )

            if (
                self.selected_source is not None
                and self.selected_source[0]
                == MoveType.FOUNDATION_TO_TABLEAU
                and self.selected_source[1] == foundation_index
            ):
                self._draw_selection(x, TOP_ROW_Y)

    def _draw_tableau(self) -> None:
        """Draw the seven tableau piles and their cards."""
        for tableau_index, pile in enumerate(self.game.tableau):
            x = MARGIN_X + tableau_index * (
                CARD_WIDTH + COLUMN_GAP
            )

            if pile.is_empty():
                pygame.draw.rect(
                    self.screen,
                    EMPTY_SLOT_COLOR,
                    (x, TABLEAU_Y, CARD_WIDTH, CARD_HEIGHT),
                    width=CARD_BORDER_WIDTH,
                    border_radius=CARD_CORNER_RADIUS,
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
            SELECTION_COLOR,
            (x, y, CARD_WIDTH, CARD_HEIGHT),
            width=SELECTION_BORDER_WIDTH,
            border_radius=CARD_CORNER_RADIUS,
        )


def main() -> None:
    """Start the Klondike graphical interface."""
    gui = KlondikeGUI()
    gui.run()


if __name__ == "__main__":
    main()