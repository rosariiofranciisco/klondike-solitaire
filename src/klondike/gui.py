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
    INVALID_MOVE_BLINK_INTERVAL,
    INVALID_MOVE_BORDER_WIDTH,
    INVALID_MOVE_COLOR,
    INVALID_MOVE_FEEDBACK_DURATION,
    MARGIN_X,
    NEW_GAME_BUTTON_COLOR,
    NEW_GAME_BUTTON_HEIGHT,
    NEW_GAME_BUTTON_HOVER_COLOR,
    NEW_GAME_BUTTON_TEXT_COLOR,
    NEW_GAME_BUTTON_WIDTH,
    NEW_GAME_BUTTON_X,
    NEW_GAME_BUTTON_Y,
    RANK_LABELS,
    RED_CARD_COLOR,
    RED_SUITS,
    RESULT_FONT_SIZE,
    RESULT_PANEL_COLOR,
    RESULT_PANEL_HEIGHT,
    RESULT_PANEL_WIDTH,
    RESULT_TEXT_COLOR,
    SELECTION_BORDER_WIDTH,
    SELECTION_COLOR,
    SUIT_FONT_NAME,
    SUIT_FONT_SIZE,
    TABLEAU_CARD_OFFSET,
    TABLEAU_Y,
    TOP_ROW_Y,
    UNDO_BUTTON_COLOR,
    UNDO_BUTTON_DISABLED_COLOR,
    UNDO_BUTTON_HEIGHT,
    UNDO_BUTTON_HOVER_COLOR,
    UNDO_BUTTON_TEXT_COLOR,
    UNDO_BUTTON_WIDTH,
    UNDO_BUTTON_X,
    UNDO_BUTTON_Y,
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
        self.result_font = pygame.font.SysFont(
            FONT_NAME,
            RESULT_FONT_SIZE,
            bold=True,
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

        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.timer_running = True

        self.running = True

        self.selected_source: tuple[MoveType, int, int | None] | None = None

        self.dragging = False
        self.drag_position: tuple[int, int] | None = None
        self.drag_offset: tuple[int, int] = (0, 0)

        self.feedback_rect: pygame.Rect | None = None
        self.feedback_until = 0

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

            elif event.type == pygame.MOUSEMOTION:
                if self.selected_source is not None and event.buttons[0]:
                    if self.drag_position is not None:
                        dx = event.pos[0] - self.drag_position[0]
                        dy = event.pos[1] - self.drag_position[1]

                        if dx * dx + dy * dy > 25:
                            self.dragging = True

                    self.drag_position = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    self._handle_drop(event.pos)

    def _handle_left_click(self, position: tuple[int, int]) -> None:
        """Handle a left mouse button click."""
        x, y = position

        undo_button_rect = pygame.Rect(
            UNDO_BUTTON_X,
            UNDO_BUTTON_Y,
            UNDO_BUTTON_WIDTH,
            UNDO_BUTTON_HEIGHT,
        )

        if undo_button_rect.collidepoint(position):
            if self.game.undo():
                self.selected_source = None
                self.dragging = False
                self.drag_position = None
                self.feedback_rect = None

            return

        new_game_button_rect = pygame.Rect(
            NEW_GAME_BUTTON_X,
            NEW_GAME_BUTTON_Y,
            NEW_GAME_BUTTON_WIDTH,
            NEW_GAME_BUTTON_HEIGHT,
        )

        if new_game_button_rect.collidepoint(position):
            self.game.start_new_game()

            self.start_time = pygame.time.get_ticks()
            self.elapsed_time = 0
            self.timer_running = True

            self.selected_source = None
            self.dragging = False
            self.drag_position = None
            self.feedback_rect = None
            self.feedback_until = 0
            return

        if self.game.is_won() or self.game.is_game_over():
            self.selected_source = None
            return

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
                self._start_drag(
                    (MoveType.WASTE_TO_TABLEAU, 0, None),
                    position,
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
                            self._start_drag(
                                (MoveType.FOUNDATION_TO_TABLEAU, index, None),
                                position,
                            )
                    else:
                        source_type, source_index, card_index = (
                            self.selected_source
                        )

                        if source_type == MoveType.WASTE_TO_TABLEAU:
                            self._execute_move(
                                Move(
                                    move_type=MoveType.WASTE_TO_FOUNDATION,
                                    target_index=index,
                                )
                            )
                            self.selected_source = None

                        elif source_type == MoveType.TABLEAU_TO_TABLEAU:
                            self._execute_move(
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
                        self._start_drag(
                            (MoveType.TABLEAU_TO_TABLEAU, column, card_index),
                            position,
                        )
                        return

            return

        source_type, source_index, card_index = self.selected_source

        if source_type == MoveType.FOUNDATION_TO_TABLEAU:
            self._execute_move(
                Move(
                    move_type=MoveType.FOUNDATION_TO_TABLEAU,
                    source_index=source_index,
                    target_index=column,
                )
            )

        elif source_type == MoveType.WASTE_TO_TABLEAU:
            self._execute_move(
                Move(
                    move_type=MoveType.WASTE_TO_TABLEAU,
                    source_index=source_index,
                    target_index=column,
                )
            )

        elif source_type == MoveType.TABLEAU_TO_TABLEAU:
            if source_index != column:
                self._execute_move(
                    Move(
                        move_type=MoveType.TABLEAU_TO_TABLEAU,
                        source_index=source_index,
                        card_index=card_index,
                        target_index=column,
                    )
                )

        self.selected_source = None

    def _start_drag(
        self,
        source: tuple[MoveType, int, int | None],
        position: tuple[int, int],
    ) -> None:
        """Start dragging a card or sequence of cards."""
        source_type, source_index, card_index = source

        if source_type == MoveType.TABLEAU_TO_TABLEAU:
            card_x = MARGIN_X + source_index * (
                CARD_WIDTH + COLUMN_GAP
            )
            card_y = TABLEAU_Y + card_index * TABLEAU_CARD_OFFSET

        elif source_type == MoveType.WASTE_TO_TABLEAU:
            card_x = MARGIN_X + CARD_WIDTH + CARD_SLOT_GAP
            card_y = TOP_ROW_Y

        else:
            foundation_start_x = (
                WINDOW_WIDTH
                - MARGIN_X
                - (
                    FOUNDATION_COUNT * CARD_WIDTH
                    + (FOUNDATION_COUNT - 1) * CARD_SLOT_GAP
                )
            )

            card_x = foundation_start_x + source_index * (
                CARD_WIDTH + CARD_SLOT_GAP
            )
            card_y = TOP_ROW_Y

        self.drag_offset = (
            position[0] - card_x,
            position[1] - card_y,
        )

        self.selected_source = source
        self.dragging = False
        self.drag_position = position

    def _handle_drop(self, position: tuple[int, int]) -> None:
        """Handle dropping a dragged card or sequence."""
        if self.selected_source is None:
            self.dragging = False
            self.drag_position = None
            return
        source_type, source_index, card_index = self.selected_source
        x, y = position

        if TOP_ROW_Y <= y <= TOP_ROW_Y + CARD_HEIGHT:
            foundation_start_x = (
                WINDOW_WIDTH
                - MARGIN_X
                - (
                    FOUNDATION_COUNT * CARD_WIDTH
                    + (FOUNDATION_COUNT - 1) * CARD_SLOT_GAP
                )
            )

            for index in range(FOUNDATION_COUNT):
                foundation_x = foundation_start_x + index * (
                    CARD_WIDTH + CARD_SLOT_GAP
                )

                if foundation_x <= x <= foundation_x + CARD_WIDTH:
                    if source_type == MoveType.WASTE_TO_TABLEAU:
                        self._execute_move(
                            Move(
                                MoveType.WASTE_TO_FOUNDATION,
                                target_index=index,
                            )
                        )

                    elif source_type == MoveType.TABLEAU_TO_TABLEAU:
                        self._execute_move(
                            Move(
                                MoveType.TABLEAU_TO_FOUNDATION,
                                source_index=source_index,
                                target_index=index,
                            )
                        )

                    break

        elif y >= TABLEAU_Y:
            column_width = CARD_WIDTH + COLUMN_GAP
            column = (x - MARGIN_X) // column_width

            if (
                0 <= column < len(self.game.tableau)
                and MARGIN_X + column * column_width
                <= x
                <= MARGIN_X + column * column_width + CARD_WIDTH
            ):
                if source_type == MoveType.FOUNDATION_TO_TABLEAU:
                    self._execute_move(
                        Move(
                            MoveType.FOUNDATION_TO_TABLEAU,
                            source_index=source_index,
                            target_index=column,
                        )
                    )

                elif source_type == MoveType.WASTE_TO_TABLEAU:
                    self._execute_move(
                        Move(
                            MoveType.WASTE_TO_TABLEAU,
                            source_index=source_index,
                            target_index=column,
                        )
                    )

                elif (
                    source_type == MoveType.TABLEAU_TO_TABLEAU
                    and source_index != column
                ):
                    self._execute_move(
                        Move(
                            MoveType.TABLEAU_TO_TABLEAU,
                            source_index=source_index,
                            card_index=card_index,
                            target_index=column,
                        )
                    )

        self.selected_source = None
        self.dragging = False
        self.drag_position = None

    def _execute_move(self, move: Move) -> bool:
        """Execute a move and highlight its destination if it fails."""
        target_rect = self._get_move_target_rect(move)
        success = self.game.execute_move(move)

        if success:
            self.feedback_rect = None
        else:
            self.feedback_rect = target_rect
            self.feedback_until = (
                pygame.time.get_ticks() + INVALID_MOVE_FEEDBACK_DURATION
            )

        return success

    def _get_move_target_rect(self, move: Move) -> pygame.Rect:
        """Get the rectangle of a move's destination."""
        if move.move_type in (
            MoveType.WASTE_TO_TABLEAU,
            MoveType.FOUNDATION_TO_TABLEAU,
            MoveType.TABLEAU_TO_TABLEAU,
        ):
            target_index = move.target_index
            pile = self.game.tableau[target_index]

            x = MARGIN_X + target_index * (CARD_WIDTH + COLUMN_GAP)

            if pile.is_empty():
                y = TABLEAU_Y
            else:
                y = TABLEAU_Y + (len(pile.cards) - 1) * TABLEAU_CARD_OFFSET

        else:
            target_index = move.target_index

            foundation_start_x = (
                WINDOW_WIDTH
                - MARGIN_X
                - (
                    FOUNDATION_COUNT * CARD_WIDTH
                    + (FOUNDATION_COUNT - 1) * CARD_SLOT_GAP
                )
            )

            x = foundation_start_x + target_index * (
                CARD_WIDTH + CARD_SLOT_GAP
            )
            y = TOP_ROW_Y

        return pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    def _get_elapsed_time(self) -> int:
        """Return the elapsed game time in seconds."""
        if self.timer_running:
            current_time = pygame.time.get_ticks()
            return (
                self.elapsed_time
                + current_time
                - self.start_time
            ) // 1000

        return self.elapsed_time // 1000

    def _draw_feedback(self) -> None:
        """Draw a blinking red outline around an invalid move's destination."""
        if self.feedback_rect is None:
            return

        current_time = pygame.time.get_ticks()

        if current_time >= self.feedback_until:
            self.feedback_rect = None
            return

        phase = (
            current_time // INVALID_MOVE_BLINK_INTERVAL
        ) % 2

        if phase == 0:
            pygame.draw.rect(
                self.screen,
                INVALID_MOVE_COLOR,
                self.feedback_rect,
                width=INVALID_MOVE_BORDER_WIDTH,
                border_radius=CARD_CORNER_RADIUS,
            )

    def _draw_new_game_button(self) -> None:
        """Draw the new game button."""
        button_rect = pygame.Rect(
            NEW_GAME_BUTTON_X,
            NEW_GAME_BUTTON_Y,
            NEW_GAME_BUTTON_WIDTH,
            NEW_GAME_BUTTON_HEIGHT,
        )

        mouse_position = pygame.mouse.get_pos()

        if button_rect.collidepoint(mouse_position):
            button_color = NEW_GAME_BUTTON_HOVER_COLOR
        else:
            button_color = NEW_GAME_BUTTON_COLOR

        pygame.draw.rect(
            self.screen,
            button_color,
            button_rect,
            border_radius=5,
        )

        text_surface = self.rank_font.render(
            "New Game",
            True,
            NEW_GAME_BUTTON_TEXT_COLOR,
        )

        text_rect = text_surface.get_rect(
            center=button_rect.center,
        )

        self.screen.blit(text_surface, text_rect)

    def _draw_undo_button(self) -> None:
        """Draw the undo button."""
        button_rect = pygame.Rect(
            UNDO_BUTTON_X,
            UNDO_BUTTON_Y,
            UNDO_BUTTON_WIDTH,
            UNDO_BUTTON_HEIGHT,
        )

        mouse_position = pygame.mouse.get_pos()
        can_undo = bool(self.game.history)

        if not can_undo:
            button_color = UNDO_BUTTON_DISABLED_COLOR
        elif button_rect.collidepoint(mouse_position):
            button_color = UNDO_BUTTON_HOVER_COLOR
        else:
            button_color = UNDO_BUTTON_COLOR

        pygame.draw.rect(
            self.screen,
            button_color,
            button_rect,
            border_radius=5,
        )

        text_surface = self.rank_font.render(
            "Undo",
            True,
            UNDO_BUTTON_TEXT_COLOR,
        )

        text_rect = text_surface.get_rect(
            center=button_rect.center,
        )

        self.screen.blit(text_surface, text_rect)

    def _draw_result(self) -> None:
        """Draw the game result when the game ends."""
        if self.game.is_won():
            message = "You Won!"
        elif self.game.is_game_over():
            message = "No More Moves!"
        else:
            return

        panel = pygame.Surface(
            (RESULT_PANEL_WIDTH, RESULT_PANEL_HEIGHT),
            pygame.SRCALPHA,
        )
        panel.fill(RESULT_PANEL_COLOR)

        panel_rect = panel.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )

        self.screen.blit(panel, panel_rect)

        text_surface = self.result_font.render(
            message,
            True,
            RESULT_TEXT_COLOR,
        )

        text_rect = text_surface.get_rect(
            center=panel_rect.center,
        )

        self.screen.blit(text_surface, text_rect)

    def _draw_move_count(self) -> None:
        """Draw the current move count."""
        text_surface = self.rank_font.render(
            f"Moves: {self.game.move_count}",
            True,
            CARD_COLOR,
        )

        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, TOP_ROW_Y - 15)
        )

        self.screen.blit(text_surface, text_rect)

    def _draw_timer(self) -> None:
        """Draw the elapsed game time."""
        elapsed_seconds = self._get_elapsed_time()

        minutes, seconds = divmod(elapsed_seconds, 60)

        text_surface = self.rank_font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True,
            CARD_COLOR,
        )

        text_rect = text_surface.get_rect(
            midright=(
                WINDOW_WIDTH - MARGIN_X,
                TOP_ROW_Y - 15,
            )
        )

        self.screen.blit(text_surface, text_rect)

    def _draw_dragged_cards(self) -> None:
        """Draw the dragged card or sequence at the mouse position."""
        if not self.dragging or self.drag_position is None:
            return

        source_type, source_index, card_index = self.selected_source

        x = self.drag_position[0] - self.drag_offset[0]
        y = self.drag_position[1] - self.drag_offset[1]

        if source_type == MoveType.TABLEAU_TO_TABLEAU:
            cards = self.game.tableau[source_index].cards[card_index:]

        elif source_type == MoveType.WASTE_TO_TABLEAU:
            cards = [self.game.waste.peek()]

        else:
            cards = [self.game.foundations[source_index].peek()]

        for index, card in enumerate(cards):
            self._draw_card(
                card,
                x,
                y + index * TABLEAU_CARD_OFFSET,
            )

    def _draw(self) -> None:
        """Draw the current game state."""
        self.screen.fill(BACKGROUND_COLOR)

        if self.timer_running and (
            self.game.is_won() or self.game.is_game_over()
        ):
            self.elapsed_time += (
                pygame.time.get_ticks() - self.start_time
            )
            self.timer_running = False

        self._draw_top_row()
        self._draw_move_count()
        self._draw_timer()
        self._draw_tableau()
        self._draw_feedback()
        self._draw_new_game_button()
        self._draw_undo_button()
        self._draw_dragged_cards()
        self._draw_result()

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
            is_dragged = (
                self.dragging
                and self.selected_source is not None
                and self.selected_source[0] == MoveType.WASTE_TO_TABLEAU
            )

            if not is_dragged:
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
            and not self.dragging
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
                is_dragged = (
                    self.dragging
                    and self.selected_source is not None
                    and self.selected_source[0] == MoveType.FOUNDATION_TO_TABLEAU
                    and self.selected_source[1] == foundation_index
                )

                if not is_dragged:
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
                and not self.dragging
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

                is_dragged = (
                    self.dragging
                    and self.selected_source is not None
                    and self.selected_source[0] == MoveType.TABLEAU_TO_TABLEAU
                    and self.selected_source[1] == tableau_index
                    and card_index >= self.selected_source[2]
                )

                if not is_dragged:
                    if card.face_up:
                        self._draw_card(card, x, y)
                    else:
                        self._draw_card_back(x, y)

                if (
                    self.selected_source is not None
                    and self.selected_source[0] == MoveType.TABLEAU_TO_TABLEAU
                    and self.selected_source[1] == tableau_index
                    and self.selected_source[2] == card_index
                    and not self.dragging
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
