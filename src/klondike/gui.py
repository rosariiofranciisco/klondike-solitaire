"""Pygame graphical interface for Klondike Solitaire."""


import pygame

from klondike.audio import GameAudio
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
    OPTIONS_AUDIO_FILL_COLOR,
    OPTIONS_AUDIO_KNOB_COLOR,
    OPTIONS_AUDIO_SLIDER_HEIGHT,
    OPTIONS_AUDIO_SLIDER_KNOB_RADIUS,
    OPTIONS_AUDIO_SLIDER_WIDTH,
    OPTIONS_AUDIO_SLIDER_X_OFFSET,
    OPTIONS_AUDIO_TEXT_COLOR,
    OPTIONS_AUDIO_TITLE_Y_OFFSET,
    OPTIONS_AUDIO_TOGGLE_HEIGHT,
    OPTIONS_AUDIO_TOGGLE_WIDTH,
    OPTIONS_AUDIO_TOGGLE_X_OFFSET,
    OPTIONS_AUDIO_TRACK_COLOR,
    OPTIONS_BUTTON_HEIGHT,
    OPTIONS_BUTTON_WIDTH,
    OPTIONS_BUTTON_X,
    OPTIONS_BUTTON_Y,
    OPTIONS_CHOICE_BUTTON_COLOR,
    OPTIONS_CHOICE_BUTTON_GAP,
    OPTIONS_CHOICE_BUTTON_HEIGHT,
    OPTIONS_CHOICE_BUTTON_HOVER_COLOR,
    OPTIONS_CHOICE_BUTTON_LABEL_GAP,
    OPTIONS_CHOICE_BUTTON_SELECTED_COLOR,
    OPTIONS_CHOICE_BUTTON_TEXT_COLOR,
    OPTIONS_CHOICE_BUTTON_WIDTH,
    OPTIONS_DRAW_MODE_Y_OFFSET,
    OPTIONS_MUSIC_Y_OFFSET,
    OPTIONS_PANEL_BORDER_COLOR,
    OPTIONS_PANEL_BORDER_WIDTH,
    OPTIONS_PANEL_COLOR,
    OPTIONS_PANEL_CORNER_RADIUS,
    OPTIONS_PANEL_HEIGHT,
    OPTIONS_PANEL_TITLE_COLOR,
    OPTIONS_PANEL_TITLE_Y_OFFSET,
    OPTIONS_PANEL_WIDTH,
    OPTIONS_RECYCLES_Y_OFFSET,
    OPTIONS_SECTION_LABEL_COLOR,
    OPTIONS_SOUND_Y_OFFSET,
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

        self.audio = GameAudio()
        self.audio.load_sounds()
        self.audio.play_music()

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
        self.result_sound_played = False

        self.running = True

        self.selected_source: tuple[MoveType, int, int | None] | None = None

        self.options_open = False

        self.dragging = False
        self.drag_position: tuple[int, int] | None = None
        self.drag_offset: tuple[int, int] = (0, 0)
        self.dragging_audio_slider: str | None = None

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
                if self.dragging_audio_slider is not None and event.buttons[0]:
                    self._update_audio_slider(event.pos)

                elif self.selected_source is not None and event.buttons[0]:
                    if self.drag_position is not None:
                        dx = event.pos[0] - self.drag_position[0]
                        dy = event.pos[1] - self.drag_position[1]

                        if dx * dx + dy * dy > 25:
                            self.dragging = True

                    self.drag_position = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.dragging_audio_slider is not None:
                        self.dragging_audio_slider = None

                    elif self.dragging:
                        self._handle_drop(event.pos)
    
    def _handle_left_click(self, position: tuple[int, int]) -> None:
        """Handle a left mouse button click."""
        x, y = position

        if self.options_open:
            options_rect = pygame.Rect(
                OPTIONS_BUTTON_X,
                OPTIONS_BUTTON_Y,
                OPTIONS_BUTTON_WIDTH,
                OPTIONS_BUTTON_HEIGHT,
            )

            if options_rect.collidepoint(position):
                self.options_open = False
                return

            self._handle_options_click(position)
            return

        undo_button_rect = pygame.Rect(
            UNDO_BUTTON_X,
            UNDO_BUTTON_Y,
            UNDO_BUTTON_WIDTH,
            UNDO_BUTTON_HEIGHT,
        )

        if undo_button_rect.collidepoint(position):
            self.audio.play_sound("click")

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
            self.audio.play_sound("click")
            self.game.start_new_game()

            self.start_time = pygame.time.get_ticks()
            self.elapsed_time = 0
            self.timer_running = True
            self.result_sound_played = False

            self.selected_source = None
            self.dragging = False
            self.drag_position = None
            self.feedback_rect = None
            self.feedback_until = 0
            return

        options_rect = pygame.Rect(
            OPTIONS_BUTTON_X,
            OPTIONS_BUTTON_Y,
            OPTIONS_BUTTON_WIDTH,
            OPTIONS_BUTTON_HEIGHT,
        )

        if options_rect.collidepoint(position):
            self.audio.play_sound("click")
            self.options_open = not self.options_open
            self.selected_source = None
            return

        if self.game.is_won() or self.game.is_game_over():
            self.selected_source = None
            return

        stock_x = MARGIN_X
        stock_y = TOP_ROW_Y
        waste_x = MARGIN_X + CARD_WIDTH + CARD_SLOT_GAP
        waste_visible_offset = max(0, min(len(self.game.waste), 3) - 1) * 15


        if (
            stock_x <= x <= stock_x + CARD_WIDTH
            and stock_y <= y <= stock_y + CARD_HEIGHT
        ):
            if self.game.stock.is_empty():
                success = self.game.execute_move(
                    Move(MoveType.RECYCLE_WASTE_TO_STOCK)
                )
            else:
                success = self.game.execute_move(
                    Move(MoveType.STOCK_TO_WASTE)
                )

            if success:
                self.audio.play_sound("draw")
                self._play_result_sound()

            self.selected_source = None
            return


        if (
            waste_x <= x <= waste_x + CARD_WIDTH + waste_visible_offset
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
            card_x = (
                MARGIN_X
                + CARD_WIDTH
                + CARD_SLOT_GAP
                + (min(len(self.game.waste), 3) - 1) * 15
            )
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

    def _play_result_sound(self) -> None:
        """Play the appropriate sound when the game ends."""
        if self.result_sound_played:
            return

        if self.game.is_won():
            self.audio.play_sound("victory")
            self.result_sound_played = True

        elif self.game.is_game_over():
            self.audio.play_sound("game_over")
            self.result_sound_played = True

    def _execute_move(self, move: Move) -> bool:
        """Execute a move and highlight its destination if it fails."""
        target_rect = self._get_move_target_rect(move)
        reveals_card = False

        if move.move_type == MoveType.TABLEAU_TO_FOUNDATION:
            source = self.game.tableau[move.source_index]

            if len(source.cards) >= 2:
                reveals_card = not source.cards[-2].face_up

        elif move.move_type == MoveType.TABLEAU_TO_TABLEAU:
            source = self.game.tableau[move.source_index]

            if move.card_index > 0:
                reveals_card = not source.cards[move.card_index - 1].face_up

        success = self.game.execute_move(move)

        if success:
            self.audio.play_sound("move")
            if reveals_card:
                self.audio.play_sound("flip")
            self._play_result_sound()
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

    def _draw_options_button(self) -> None:
        """Draw the Options button."""
        button_rect = pygame.Rect(
            OPTIONS_BUTTON_X,
            OPTIONS_BUTTON_Y,
            OPTIONS_BUTTON_WIDTH,
            OPTIONS_BUTTON_HEIGHT,
        )

        mouse_position = pygame.mouse.get_pos()
        color = (
            NEW_GAME_BUTTON_HOVER_COLOR
            if button_rect.collidepoint(mouse_position)
            else NEW_GAME_BUTTON_COLOR
        )

        pygame.draw.rect(
            self.screen,
            color,
            button_rect,
            border_radius=8,
        )

        text = self.rank_font.render(
            "Options",
            True,
            NEW_GAME_BUTTON_TEXT_COLOR,
        )

        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)

    def _draw_option_button(
        self,
        text: str,
        x: int,
        y: int,
        selected: bool,
    ) -> None:
        """Draw an option button."""
        button_rect = pygame.Rect(
            x,
            y,
            OPTIONS_CHOICE_BUTTON_WIDTH,
            OPTIONS_CHOICE_BUTTON_HEIGHT,
        )

        mouse_position = pygame.mouse.get_pos()

        if selected:
            color = OPTIONS_CHOICE_BUTTON_SELECTED_COLOR
        elif button_rect.collidepoint(mouse_position):
            color = OPTIONS_CHOICE_BUTTON_HOVER_COLOR
        else:
            color = OPTIONS_CHOICE_BUTTON_COLOR

        pygame.draw.rect(
            self.screen,
            color,
            button_rect,
            border_radius=6,
        )

        label = self.rank_font.render(
            text,
            True,
            OPTIONS_CHOICE_BUTTON_TEXT_COLOR,
        )

        label_rect = label.get_rect(center=button_rect.center)
        self.screen.blit(label, label_rect)

    def _update_audio_slider(self, position: tuple[int, int]) -> None:
        """Update the volume of the audio slider being dragged."""
        panel_left = (WINDOW_WIDTH - OPTIONS_PANEL_WIDTH) // 2
        panel_top = (WINDOW_HEIGHT - OPTIONS_PANEL_HEIGHT) // 2

        if self.dragging_audio_slider == "music":
            slider_x = panel_left + OPTIONS_AUDIO_SLIDER_X_OFFSET
            slider_y = (
                panel_top
                + OPTIONS_MUSIC_Y_OFFSET
                - OPTIONS_AUDIO_SLIDER_HEIGHT // 2
            )

            slider_rect = pygame.Rect(
                slider_x,
                slider_y,
                OPTIONS_AUDIO_SLIDER_WIDTH,
                OPTIONS_AUDIO_SLIDER_HEIGHT,
            )

            volume = (position[0] - slider_rect.left) / slider_rect.width
            self.audio.set_music_volume(volume)

        elif self.dragging_audio_slider == "sound":
            slider_x = panel_left + OPTIONS_AUDIO_SLIDER_X_OFFSET
            slider_y = (
                panel_top
                + OPTIONS_SOUND_Y_OFFSET
                - OPTIONS_AUDIO_SLIDER_HEIGHT // 2
            )

            slider_rect = pygame.Rect(
                slider_x,
                slider_y,
                OPTIONS_AUDIO_SLIDER_WIDTH,
                OPTIONS_AUDIO_SLIDER_HEIGHT,
            )

            volume = (position[0] - slider_rect.left) / slider_rect.width
            self.audio.set_sound_volume(volume)

    def _handle_options_click(self, position: tuple[int, int]) -> bool:
        """Handle clicks on the options panel."""
        panel_rect = pygame.Rect(
            (WINDOW_WIDTH - OPTIONS_PANEL_WIDTH) // 2,
            (WINDOW_HEIGHT - OPTIONS_PANEL_HEIGHT) // 2,
            OPTIONS_PANEL_WIDTH,
            OPTIONS_PANEL_HEIGHT,
        )

        if not panel_rect.collidepoint(position):
            return True

        music_y = panel_rect.top + OPTIONS_MUSIC_Y_OFFSET
        sound_y = panel_rect.top + OPTIONS_SOUND_Y_OFFSET

        music_slider_rect = pygame.Rect(
            panel_rect.left + OPTIONS_AUDIO_SLIDER_X_OFFSET,
            music_y - OPTIONS_AUDIO_SLIDER_HEIGHT // 2 - 8,
            OPTIONS_AUDIO_SLIDER_WIDTH,
            OPTIONS_AUDIO_SLIDER_HEIGHT + 16,
        )

        sound_slider_rect = pygame.Rect(
            panel_rect.left + OPTIONS_AUDIO_SLIDER_X_OFFSET,
            sound_y - OPTIONS_AUDIO_SLIDER_HEIGHT // 2 - 8,
            OPTIONS_AUDIO_SLIDER_WIDTH,
            OPTIONS_AUDIO_SLIDER_HEIGHT + 16,
        )

        if music_slider_rect.collidepoint(position):
            self.dragging_audio_slider = "music"
            self._update_audio_slider(position)
            return True

        if sound_slider_rect.collidepoint(position):
            self.dragging_audio_slider = "sound"
            self._update_audio_slider(position)
            return True

        music_y = panel_rect.top + OPTIONS_MUSIC_Y_OFFSET
        sound_y = panel_rect.top + OPTIONS_SOUND_Y_OFFSET

        music_toggle_rect = pygame.Rect(
            panel_rect.left + OPTIONS_AUDIO_TOGGLE_X_OFFSET,
            music_y - OPTIONS_AUDIO_TOGGLE_HEIGHT // 2,
            OPTIONS_AUDIO_TOGGLE_WIDTH,
            OPTIONS_AUDIO_TOGGLE_HEIGHT,
        )

        sound_toggle_rect = pygame.Rect(
            panel_rect.left + OPTIONS_AUDIO_TOGGLE_X_OFFSET,
            sound_y - OPTIONS_AUDIO_TOGGLE_HEIGHT // 2,
            OPTIONS_AUDIO_TOGGLE_WIDTH,
            OPTIONS_AUDIO_TOGGLE_HEIGHT,
        )

        if music_toggle_rect.collidepoint(position):
            self.audio.toggle_music()

        elif sound_toggle_rect.collidepoint(position):
            self.audio.toggle_sound()

        draw_button_y = (
            panel_rect.top
            + OPTIONS_DRAW_MODE_Y_OFFSET
            + OPTIONS_CHOICE_BUTTON_LABEL_GAP
        )

        recycles_button_y = (
            panel_rect.top
            + OPTIONS_RECYCLES_Y_OFFSET
            + OPTIONS_CHOICE_BUTTON_LABEL_GAP
        )

        buttons_width = (
            OPTIONS_CHOICE_BUTTON_WIDTH * 2
            + OPTIONS_CHOICE_BUTTON_GAP
        )

        button_start_x = (WINDOW_WIDTH - buttons_width) // 2

        draw_1_rect = pygame.Rect(
            button_start_x,
            draw_button_y,
            OPTIONS_CHOICE_BUTTON_WIDTH,
            OPTIONS_CHOICE_BUTTON_HEIGHT,
        )

        draw_3_rect = pygame.Rect(
            button_start_x + OPTIONS_CHOICE_BUTTON_WIDTH + OPTIONS_CHOICE_BUTTON_GAP,
            draw_button_y,
            OPTIONS_CHOICE_BUTTON_WIDTH,
            OPTIONS_CHOICE_BUTTON_HEIGHT,
        )

        unlimited_rect = pygame.Rect(
            button_start_x,
            recycles_button_y,
            OPTIONS_CHOICE_BUTTON_WIDTH,
            OPTIONS_CHOICE_BUTTON_HEIGHT,
        )

        passes_rect = pygame.Rect(
            button_start_x + OPTIONS_CHOICE_BUTTON_WIDTH + OPTIONS_CHOICE_BUTTON_GAP,
            recycles_button_y,
            OPTIONS_CHOICE_BUTTON_WIDTH,
            OPTIONS_CHOICE_BUTTON_HEIGHT,
        )

        if draw_1_rect.collidepoint(position):
            self.game.draw_count = 1

        elif draw_3_rect.collidepoint(position):
            self.game.draw_count = 3

        elif unlimited_rect.collidepoint(position):
            self.game.max_recycles = None

        elif passes_rect.collidepoint(position):
            self.game.max_recycles = 3

        return True

    def _draw_audio_toggle(
        self,
        text: str,
        x: int,
        y: int,
        enabled: bool,
    ) -> None:
        """Draw an audio on/off toggle button."""
        button_rect = pygame.Rect(
            x,
            y,
            OPTIONS_AUDIO_TOGGLE_WIDTH,
            OPTIONS_AUDIO_TOGGLE_HEIGHT,
        )

        color = (
            OPTIONS_CHOICE_BUTTON_SELECTED_COLOR
            if enabled
            else OPTIONS_CHOICE_BUTTON_COLOR
        )

        pygame.draw.rect(
            self.screen,
            color,
            button_rect,
            border_radius=5,
        )

        label = self.rank_font.render(
            text,
            True,
            OPTIONS_AUDIO_TEXT_COLOR,
        )

        label_rect = label.get_rect(center=button_rect.center)
        self.screen.blit(label, label_rect)

    def _draw_audio_slider(
        self,
        x: int,
        y: int,
        volume: float,
    ) -> None:
        """Draw an audio volume slider."""
        slider_rect = pygame.Rect(
            x,
            y,
            OPTIONS_AUDIO_SLIDER_WIDTH,
            OPTIONS_AUDIO_SLIDER_HEIGHT,
        )

        pygame.draw.rect(
            self.screen,
            OPTIONS_AUDIO_TRACK_COLOR,
            slider_rect,
            border_radius=5,
        )

        fill_width = int(
            OPTIONS_AUDIO_SLIDER_WIDTH * volume
        )

        if fill_width > 0:
            pygame.draw.rect(
                self.screen,
                OPTIONS_AUDIO_FILL_COLOR,
                (
                    x,
                    y,
                    fill_width,
                    OPTIONS_AUDIO_SLIDER_HEIGHT,
                ),
                border_radius=5,
            )

        knob_x = x + fill_width
        knob_y = y + OPTIONS_AUDIO_SLIDER_HEIGHT // 2

        pygame.draw.circle(
            self.screen,
            OPTIONS_AUDIO_KNOB_COLOR,
            (knob_x, knob_y),
            OPTIONS_AUDIO_SLIDER_KNOB_RADIUS,
        )

    def _draw_options_panel(self) -> None:
        """Draw the game options panel."""
        panel_rect = pygame.Rect(
            (WINDOW_WIDTH - OPTIONS_PANEL_WIDTH) // 2,
            (WINDOW_HEIGHT - OPTIONS_PANEL_HEIGHT) // 2,
            OPTIONS_PANEL_WIDTH,
            OPTIONS_PANEL_HEIGHT,
        )

        pygame.draw.rect(
            self.screen,
            OPTIONS_PANEL_COLOR,
            panel_rect,
            border_radius=OPTIONS_PANEL_CORNER_RADIUS,
        )

        pygame.draw.rect(
            self.screen,
            OPTIONS_PANEL_BORDER_COLOR,
            panel_rect,
            width=OPTIONS_PANEL_BORDER_WIDTH,
            border_radius=OPTIONS_PANEL_CORNER_RADIUS,
        )

        title = self.rank_font.render(
            "Game Options",
            True,
            OPTIONS_PANEL_TITLE_COLOR,
        )

        title_rect = title.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                panel_rect.top + OPTIONS_PANEL_TITLE_Y_OFFSET,
            )
        )

        self.screen.blit(title, title_rect)

        draw_mode_label = self.rank_font.render(
            "Draw Mode",
            True,
            OPTIONS_SECTION_LABEL_COLOR,
        )

        draw_mode_rect = draw_mode_label.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                panel_rect.top + OPTIONS_DRAW_MODE_Y_OFFSET,
            )
        )

        self.screen.blit(draw_mode_label, draw_mode_rect)

        draw_button_y = (
            panel_rect.top
            + OPTIONS_DRAW_MODE_Y_OFFSET
            + OPTIONS_CHOICE_BUTTON_LABEL_GAP
        )

        draw_buttons_width = (
            OPTIONS_CHOICE_BUTTON_WIDTH * 2
            + OPTIONS_CHOICE_BUTTON_GAP
        )

        draw_button_start_x = (
            WINDOW_WIDTH - draw_buttons_width
        ) // 2

        self._draw_option_button(
            "Draw 1",
            draw_button_start_x,
            draw_button_y,
            self.game.draw_count == 1,
        )

        self._draw_option_button(
            "Draw 3",
            draw_button_start_x
            + OPTIONS_CHOICE_BUTTON_WIDTH
            + OPTIONS_CHOICE_BUTTON_GAP,
            draw_button_y,
            self.game.draw_count == 3,
        )

        recycles_button_y = (
            panel_rect.top
            + OPTIONS_RECYCLES_Y_OFFSET
            + OPTIONS_CHOICE_BUTTON_LABEL_GAP
        )

        recycles_buttons_width = (
            OPTIONS_CHOICE_BUTTON_WIDTH * 2
            + OPTIONS_CHOICE_BUTTON_GAP
        )

        recycles_button_start_x = (
            WINDOW_WIDTH - recycles_buttons_width
        ) // 2

        self._draw_option_button(
            "Unlimited",
            recycles_button_start_x,
            recycles_button_y,
            self.game.max_recycles is None,
        )

        self._draw_option_button(
            "3 Passes",
            recycles_button_start_x
            + OPTIONS_CHOICE_BUTTON_WIDTH
            + OPTIONS_CHOICE_BUTTON_GAP,
            recycles_button_y,
            self.game.max_recycles == 3,
        )        

        recycles_label = self.rank_font.render(
            "Stock Recycles",
            True,
            OPTIONS_SECTION_LABEL_COLOR,
        )

        recycles_rect = recycles_label.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                panel_rect.top + OPTIONS_RECYCLES_Y_OFFSET,
            )
        )

        self.screen.blit(recycles_label, recycles_rect)

        audio_title = self.rank_font.render(
            "Audio Settings",
            True,
            OPTIONS_SECTION_LABEL_COLOR,
        )

        audio_title_rect = audio_title.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                panel_rect.top + OPTIONS_AUDIO_TITLE_Y_OFFSET,
            )
        )

        self.screen.blit(audio_title, audio_title_rect)

        music_y = panel_rect.top + OPTIONS_MUSIC_Y_OFFSET
        sound_y = panel_rect.top + OPTIONS_SOUND_Y_OFFSET

        music_label = self.rank_font.render(
            "Music",
            True,
            OPTIONS_AUDIO_TEXT_COLOR,
        )

        music_label_rect = music_label.get_rect(
            midleft=(panel_rect.left + 25, music_y),
        )

        self.screen.blit(music_label, music_label_rect)

        self._draw_audio_toggle(
            "On" if self.audio.music_enabled else "Off",
            panel_rect.left + OPTIONS_AUDIO_TOGGLE_X_OFFSET,
            music_y - OPTIONS_AUDIO_TOGGLE_HEIGHT // 2,
            self.audio.music_enabled,
        )

        self._draw_audio_slider(
            panel_rect.left + OPTIONS_AUDIO_SLIDER_X_OFFSET,
            music_y - OPTIONS_AUDIO_SLIDER_HEIGHT // 2,
            self.audio.music_volume,
        )

        sound_label = self.rank_font.render(
            "Sound FX",
            True,
            OPTIONS_AUDIO_TEXT_COLOR,
        )

        sound_label_rect = sound_label.get_rect(
            midleft=(panel_rect.left + 25, sound_y),
        )

        self.screen.blit(sound_label, sound_label_rect)

        self._draw_audio_toggle(
            "On" if self.audio.sound_enabled else "Off",
            panel_rect.left + OPTIONS_AUDIO_TOGGLE_X_OFFSET,
            sound_y - OPTIONS_AUDIO_TOGGLE_HEIGHT // 2,
            self.audio.sound_enabled,
        )

        self._draw_audio_slider(
            panel_rect.left + OPTIONS_AUDIO_SLIDER_X_OFFSET,
            sound_y - OPTIONS_AUDIO_SLIDER_HEIGHT // 2,
            self.audio.sound_volume,
        )

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

    def _draw_score(self) -> None:
        """Draw the current score."""
        text_surface = self.rank_font.render(
            f"Score: {self.game.score}",
            True,
            CARD_COLOR,
        )

        text_rect = text_surface.get_rect(
            midleft=(
                MARGIN_X,
                TOP_ROW_Y - 15,
            )
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
        self._draw_score()
        self._draw_move_count()
        self._draw_timer()
        self._draw_tableau()
        self._draw_feedback()
        self._draw_new_game_button()
        self._draw_undo_button()
        self._draw_options_button()
        self._draw_dragged_cards()
        self._draw_result()

        if self.options_open:
            self._draw_options_panel()

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

            visible_cards = self.game.waste.cards[-3:]

            visible_cards = self.game.waste.cards[-3:]

            for index, card in enumerate(visible_cards):
                is_top_card = index == len(visible_cards) - 1

                if is_dragged and is_top_card:
                    continue

                card_x = waste_x + index * 15

                self._draw_card(
                    card,
                    card_x,
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
            selected_waste_x = (
                waste_x + (min(len(self.game.waste), 3) - 1) * 15
            )
            self._draw_selection(selected_waste_x, TOP_ROW_Y)

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
