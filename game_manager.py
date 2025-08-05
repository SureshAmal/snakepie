import pygame
import sys
import json
import os
from snake import SnakeGame
from constants import (
    TEXT_COLOR,
    ACCENT_COLOR,
    ERROR_COLOR,
    BUTTON_DEFAULT_COLOR,
    BUTTON_HOVER_COLOR,
    BUTTON_BORDER_COLOR,
    MIN_HEIGHT,
    MIN_WIDTH,
    font,
    big_font,
    medium_font,
    smaller_font,
)
from ui_elements import draw_button, draw_input_box


class GameManager:
    def __init__(self, surface):
        self.win = surface
        self.current_width, self.current_height = self.win.get_size()
        self.current_state = "ENTER_NAME"
        self.user_name = ""
        self.input_box_text = ""
        self.input_active = False
        self.message_text = ""
        self.message_color = TEXT_COLOR
        self.message_display_time = 0

        self.game_speed_level = "Medium"
        self.game_speed_fps = 10

        self.snake_game = SnakeGame(self.current_width, self.current_height)
        self._ensure_scores_file_exists()
        self.score_data = self._load_scores()
        self.score_display_level = "Medium"

        self.name_input_rect = None
        self.settings_input_rect = None
        self.easy_button_rect = None
        self.medium_button_rect = None
        self.hard_button_rect = None
        self.view_scores_button_rect = None
        self.settings_button_rect = None
        self.quit_button_rect = None
        self.back_button_rect = None
        self.play_again_button_rect = None
        self.easy_scores_tab_rect = None
        self.medium_scores_tab_rect = None
        self.hard_scores_tab_rect = None
        self.pause_button_rect = None
        self.focusable_elements_map = {}
        self.focused_rect = None
        self.focused_index = -1

        self._recalculate_ui_elements()
        self._set_initial_focus()

    def _recalculate_ui_elements(self):
        self.name_input_rect = pygame.Rect(
            self.current_width // 2 - 150, self.current_height // 2 - 20, 300, 40
        )
        self.settings_input_rect = pygame.Rect(
            self.current_width // 2 - 150, self.current_height // 2 + 20, 300, 40
        )
        button_width, button_height = 100, 50
        spacing = 20
        total_speed_button_width = (button_width * 3) + (spacing * 2)
        start_x_speed = (self.current_width - total_speed_button_width) // 2
        self.easy_button_rect = pygame.Rect(
            start_x_speed, self.current_height // 2 - 50, button_width, button_height
        )
        self.medium_button_rect = pygame.Rect(
            start_x_speed + button_width + spacing,
            self.current_height // 2 - 50,
            button_width,
            button_height,
        )
        self.hard_button_rect = pygame.Rect(
            start_x_speed + (button_width + spacing) * 2,
            self.current_height // 2 - 50,
            button_width,
            button_height,
        )
        self.view_scores_button_rect = pygame.Rect(
            self.current_width // 2 - 120, self.current_height // 2 + 50, 240, 50
        )
        self.settings_button_rect = pygame.Rect(
            self.current_width // 2 - 120, self.current_height // 2 + 110, 240, 50
        )
        self.quit_button_rect = pygame.Rect(
            self.current_width // 2 - 120, self.current_height // 2 + 170, 240, 50
        )
        self.back_button_rect = pygame.Rect(10, self.current_height - 60, 100, 40)
        self.play_again_button_rect = pygame.Rect(
            self.current_width // 2 - 75, self.current_height // 2 + 100, 150, 50
        )
        tab_button_width = 150
        tab_spacing = 20
        total_tab_width = (tab_button_width * 3) + (tab_spacing * 2)
        tab_start_x = (self.current_width - total_tab_width) // 2
        self.easy_scores_tab_rect = pygame.Rect(tab_start_x, 120, tab_button_width, 40)
        self.medium_scores_tab_rect = pygame.Rect(
            tab_start_x + tab_button_width + tab_spacing, 120, tab_button_width, 40
        )
        self.hard_scores_tab_rect = pygame.Rect(
            tab_start_x + (tab_button_width + tab_spacing) * 2,
            120,
            tab_button_width,
            40,
        )
        self.pause_button_rect = pygame.Rect(self.current_width - 60, 10, 40, 40)
        self.focusable_elements_map = {
            "ENTER_NAME": [self.name_input_rect],
            "SELECT_SPEED": [
                self.easy_button_rect,
                self.medium_button_rect,
                self.hard_button_rect,
                self.view_scores_button_rect,
                self.settings_button_rect,
                self.quit_button_rect,
            ],
            "GAME_OVER": [self.play_again_button_rect],
            "SCORE_HISTORY": [
                self.easy_scores_tab_rect,
                self.medium_scores_tab_rect,
                self.hard_scores_tab_rect,
                self.back_button_rect,
            ],
            "SETTINGS": [self.settings_input_rect, self.back_button_rect],
        }

    def _set_initial_focus(self):
        if self.current_state in self.focusable_elements_map:
            elements = self.focusable_elements_map[self.current_state]
            if elements:
                self.focused_index = 0
                self.focused_rect = elements[0]
                if self.focused_rect in [
                    self.name_input_rect,
                    self.settings_input_rect,
                ]:
                    self.input_active = True
                    if self.focused_rect == self.settings_input_rect:
                        self.input_box_text = self.user_name
                    elif (
                        self.focused_rect == self.name_input_rect
                        and self.current_state == "ENTER_NAME"
                    ):
                        self.input_box_text = ""
                else:
                    self.input_active = False
            else:
                self.focused_index = -1
                self.focused_rect = None
                self.input_active = False
        else:
            self.focused_index = -1
            self.focused_rect = None
            self.input_active = False
        self.message_text = ""

    def _update_focus(self, direction):
        if self.current_state not in self.focusable_elements_map:
            return

        elements = self.focusable_elements_map[self.current_state]
        num_elements = len(elements)

        if num_elements == 0:
            self.focused_index = -1
            self.focused_rect = None
            self.input_active = False
            return

        current_idx = self.focused_index if self.focused_index != -1 else 0

        if self.current_state == "SELECT_SPEED":
            if direction == "UP":
                if current_idx >= 3:
                    if current_idx == 3:
                        self.focused_index = 1
                    elif current_idx == 4:
                        self.focused_index = 3
                    elif current_idx == 5:
                        self.focused_index = 4
                else:
                    self.focused_index = (current_idx - 1 + 3) % 3
            elif direction == "DOWN":
                if current_idx < 3:
                    self.focused_index = 3
                elif current_idx >= 3:
                    self.focused_index = (current_idx + 1) % num_elements
            elif direction == "LEFT":
                if current_idx < 3:
                    self.focused_index = (current_idx - 1 + 3) % 3
                else:
                    self.focused_index = current_idx
            elif direction == "RIGHT":
                if current_idx < 3:
                    self.focused_index = (current_idx + 1) % 3
                else:
                    self.focused_index = current_idx
            else:
                self.focused_index = (
                    current_idx
                    + (1 if direction == "TAB_FORWARD" else -1)
                    + num_elements
                ) % num_elements

        elif self.current_state == "SCORE_HISTORY":
            if direction == "UP":
                if current_idx == 3:
                    self.focused_index = 1
                else:
                    self.focused_index = (current_idx - 1 + 3) % 3
            elif direction == "DOWN":
                if current_idx < 3:
                    self.focused_index = 3
                else:
                    self.focused_index = (current_idx + 1) % num_elements
            elif direction == "LEFT":
                if current_idx < 3:
                    self.focused_index = (current_idx - 1 + 3) % 3
                else:
                    self.focused_index = current_idx
            elif direction == "RIGHT":
                if current_idx < 3:
                    self.focused_index = (current_idx + 1) % 3
                else:
                    self.focused_index = current_idx
            else:
                self.focused_index = (
                    current_idx
                    + (1 if direction == "TAB_FORWARD" else -1)
                    + num_elements
                ) % num_elements

        else:
            self.focused_index = (
                current_idx + (1 if direction == "TAB_FORWARD" else -1) + num_elements
            ) % num_elements

        self.focused_rect = elements[self.focused_index]

        if self.focused_rect in [self.name_input_rect, self.settings_input_rect]:
            self.input_active = True
            if self.focused_rect == self.settings_input_rect:
                self.input_box_text = self.user_name
            elif (
                self.focused_rect == self.name_input_rect
                and self.current_state == "ENTER_NAME"
            ):
                self.input_box_text = ""
        else:
            self.input_active = False

    def _activate_focused_element(self):
        if not self.focused_rect:
            return

        if self.focused_rect == self.play_again_button_rect:
            self.current_state = "SELECT_SPEED"
            pygame.mouse.set_visible(True)
            self._set_initial_focus()
        elif self.focused_rect == self.back_button_rect:
            if self.current_state == "SETTINGS":
                self._commit_name_change(self.settings_input_rect)
            self.current_state = "SELECT_SPEED"
            pygame.mouse.set_visible(True)
            self._set_initial_focus()
        elif self.focused_rect == self.easy_button_rect:
            self._set_game_speed("Easy")
            self.snake_game.reset(self.current_width, self.current_height)
            self.current_state = "PLAYING"
            pygame.mouse.set_visible(False)
            self._set_initial_focus()
        elif self.focused_rect == self.medium_button_rect:
            self._set_game_speed("Medium")
            self.snake_game.reset(self.current_width, self.current_height)
            self.current_state = "PLAYING"
            pygame.mouse.set_visible(False)
            self._set_initial_focus()
        elif self.focused_rect == self.hard_button_rect:
            self._set_game_speed("Hard")
            self.snake_game.reset(self.current_width, self.current_height)
            self.current_state = "PLAYING"
            pygame.mouse.set_visible(False)
            self._set_initial_focus()
        elif self.focused_rect == self.view_scores_button_rect:
            self.current_state = "SCORE_HISTORY"
            self.score_display_level = self.game_speed_level
            pygame.mouse.set_visible(True)
            self._set_initial_focus()
        elif self.focused_rect == self.settings_button_rect:
            self.current_state = "SETTINGS"
            self.input_box_text = self.user_name
            pygame.mouse.set_visible(True)
            self._set_initial_focus()
        elif self.focused_rect == self.quit_button_rect:
            pygame.quit()
            sys.exit()
        elif self.focused_rect == self.easy_scores_tab_rect:
            self.score_display_level = "Easy"
        elif self.focused_rect == self.medium_scores_tab_rect:
            self.score_display_level = "Medium"
        elif self.focused_rect == self.hard_scores_tab_rect:
            self.score_display_level = "Hard"

    def _handle_menu_mouse_click(self, mouse_pos):
        clicked_element = None
        for i, rect in enumerate(
            self.focusable_elements_map.get(self.current_state, [])
        ):
            if rect and rect.collidepoint(mouse_pos):
                clicked_element = rect
                self.focused_index = i
                self.focused_rect = rect
                break

        if clicked_element:
            if clicked_element in [self.name_input_rect, self.settings_input_rect]:
                self.input_active = True
                if clicked_element == self.settings_input_rect:
                    self.input_box_text = self.user_name
                elif (
                    clicked_element == self.name_input_rect
                    and self.current_state == "ENTER_NAME"
                ):
                    self.input_box_text = ""
            else:
                if self.input_active and self.focused_rect:
                    self._commit_name_change(
                        self.settings_input_rect
                        if self.current_state == "SETTINGS"
                        else self.name_input_rect
                    )
                self.input_active = False
                self._activate_focused_element()
        else:
            if self.input_active and self.focused_rect:
                self._commit_name_change(
                    self.settings_input_rect
                    if self.current_state == "SETTINGS"
                    else self.name_input_rect
                )
            self.input_active = False
            self.focused_index = -1
            self.focused_rect = None

    def _show_message(self, text, color=TEXT_COLOR, duration=2000):
        self.message_text = text
        self.message_color = color
        self.message_display_time = pygame.time.get_ticks() + duration

    def _ensure_scores_file_exists(self):
        if not os.path.exists("scores.json") or os.path.getsize("scores.json") == 0:
            with open("scores.json", "w") as f:
                json.dump({}, f)

    def _load_scores(self):
        try:
            with open("scores.json", "r") as f:
                data = json.load(f)
                for user, user_scores_data in data.items():
                    if not isinstance(user_scores_data, dict):
                        print(f"Migrating old score format for user: {user}")
                        old_scores_list = (
                            user_scores_data
                            if isinstance(user_scores_data, list)
                            else []
                        )
                        data[user] = {"Easy": [], "Medium": [], "Hard": []}
                        data[user]["Medium"].extend(old_scores_list)
                        data[user]["Medium"].sort(reverse=True)
                    else:
                        for level in ["Easy", "Medium", "Hard"]:
                            if level not in data[user]:
                                data[user][level] = []
                            data[user][level] = sorted(
                                [
                                    s
                                    for s in data[user][level]
                                    if isinstance(s, (int, float))
                                ],
                                reverse=True,
                            )
                return data
        except json.JSONDecodeError:
            print("Scores file corrupted or empty. Resetting data.")
            with open("scores.json", "w") as f:
                json.dump({}, f)
            return {}

    def _save_scores(self):
        with open("scores.json", "w") as f:
            json.dump(self.score_data, f, indent=4)

    def _add_score(self, username, score, level):
        if username not in self.score_data:
            self.score_data[username] = {"Easy": [], "Medium": [], "Hard": []}

        if level not in self.score_data[username]:
            self.score_data[username][level] = []

        self.score_data[username][level].append(score)
        self.score_data[username][level].sort(reverse=True)
        self._save_scores()

    def _get_highest_score_for_user_and_level(self, username, level):
        user_data = self.score_data.get(username, {})
        level_scores = user_data.get(level, [])
        return max(level_scores) if level_scores else 0

    def _get_global_top_scores_for_level(self, level, num_scores=10):
        all_scores_for_level = []
        for user, levels_data in self.score_data.items():
            if level in levels_data and levels_data[level]:
                highest_for_user_on_level = max(levels_data[level])
                all_scores_for_level.append(
                    {"user": user, "score": highest_for_user_on_level}
                )

        all_scores_for_level.sort(key=lambda x: x["score"], reverse=True)
        return all_scores_for_level[:num_scores]

    def _set_game_speed(self, level):
        self.game_speed_level = level
        if level == "Easy":
            self.game_speed_fps = 5
        elif level == "Medium":
            self.game_speed_fps = 10
        elif level == "Hard":
            self.game_speed_fps = 15

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                new_width, new_height = event.size

                if new_width < MIN_WIDTH:
                    new_width = MIN_WIDTH
                if new_height < MIN_HEIGHT:
                    new_height = MIN_HEIGHT

                self.current_width, self.current_height = new_width, new_height
                self._recalculate_ui_elements()
                self.snake_game.update_dimensions(
                    self.current_width, self.current_height
                )

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            if self.current_state == "PLAYING":
                self.snake_game.handle_input(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.snake_game.paused = not self.snake_game.paused
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause_button_rect.collidepoint(event.pos):
                        self.snake_game.paused = not self.snake_game.paused
            else:
                pygame.mouse.set_visible(True)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        if self.input_active:
                            if self.focused_rect:
                                self._commit_name_change(
                                    self.name_input_rect
                                    if self.current_state == "ENTER_NAME"
                                    else self.settings_input_rect
                                )
                        self._update_focus(
                            "TAB_FORWARD"
                            if not (event.mod & pygame.KMOD_SHIFT)
                            else "TAB_BACKWARD"
                        )
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.input_active:
                            if self.focused_rect:
                                self._commit_name_change(
                                    self.name_input_rect
                                    if self.current_state == "ENTER_NAME"
                                    else self.settings_input_rect
                                )

                            if self.current_state == "ENTER_NAME":
                                if self.user_name:
                                    self.current_state = "SELECT_SPEED"
                                    self._set_initial_focus()
                                else:
                                    self._show_message(
                                        "Name cannot be empty!", ERROR_COLOR
                                    )
                        elif self.focused_rect:
                            self._activate_focused_element()
                    elif event.key in [
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ]:
                        if not self.input_active:
                            self._update_focus(pygame.key.name(event.key).upper())
                    elif event.key == pygame.K_BACKSPACE:
                        if self.input_active:
                            self.input_box_text = self.input_box_text[:-1]

                elif event.type == pygame.TEXTINPUT:
                    if self.input_active:
                        current_input_rect = self.focused_rect
                        if current_input_rect:
                            temp_surface = font.render(
                                self.input_box_text + event.text, True, TEXT_COLOR
                            )
                            if temp_surface.get_width() < current_input_rect.width - 10:
                                self.input_box_text += event.text

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_menu_mouse_click(event.pos)

    def _commit_name_change(self, input_rect):
        temp_name = self.input_box_text.strip()

        if self.current_state == "ENTER_NAME":
            if not temp_name:
                self.user_name = "Player"
            else:
                self.user_name = temp_name

            self.input_box_text = self.user_name if not temp_name else temp_name
            self.input_active = False

        elif self.current_state == "SETTINGS":
            if not temp_name:
                self._show_message("Name cannot be empty!", ERROR_COLOR)
                self.input_box_text = self.user_name
            elif temp_name != self.user_name:
                self.user_name = temp_name
                self._show_message("Name updated!", ACCENT_COLOR)
            else:
                self._show_message("No change made.", BUTTON_BORDER_COLOR)
            self.input_active = False
            self.input_box_text = self.user_name

    def update(self):
        if self.current_state == "PLAYING":
            is_game_over = self.snake_game.update()
            if is_game_over:
                self.current_state = "GAME_OVER"
                self._add_score(
                    self.user_name, self.snake_game.score, self.game_speed_level
                )
                pygame.mouse.set_visible(True)
                self._set_initial_focus()

        if self.message_text and pygame.time.get_ticks() > self.message_display_time:
            self.message_text = ""

    def draw(self):
        self.win.fill((0, 0, 0))

        if self.current_state == "ENTER_NAME":
            self._draw_name_input_screen()
        elif self.current_state == "SELECT_SPEED":
            self._draw_speed_selection_screen()
        elif self.current_state == "PLAYING":
            self.snake_game.draw(self.win, self.current_width, self.current_height)
            self._draw_pause_button()
        elif self.current_state == "GAME_OVER":
            self.snake_game.draw(self.win, self.current_width, self.current_height)
            self._draw_game_over_screen()
        elif self.current_state == "SCORE_HISTORY":
            self._draw_score_history_screen()
        elif self.current_state == "SETTINGS":
            self._draw_settings_screen()

        if self.message_text:
            message_surface = medium_font.render(
                self.message_text, True, self.message_color
            )
            message_rect = message_surface.get_rect(
                center=(self.current_width // 2, self.current_height - 50)
            )
            self.win.blit(message_surface, message_rect)

        pygame.display.update()

    def _draw_name_input_screen(self):
        self.snake_game.draw_background(
            self.win, self.current_width, self.current_height
        )

        prompt_text = big_font.render("Enter Your Name:", True, TEXT_COLOR)
        self.win.blit(
            prompt_text,
            (
                self.current_width // 2 - prompt_text.get_width() // 2,
                self.current_height // 2 - 80,
            ),
        )

        draw_input_box(
            self.win,
            self.name_input_rect,
            self.input_box_text,
            self.input_active and self.focused_rect == self.name_input_rect,
            font,
            TEXT_COLOR,
            self.focused_rect,
            default_display_text="",
        )

        hint_text = smaller_font.render(
            "Press ENTER to continue", True, (180, 180, 180)
        )
        self.win.blit(
            hint_text,
            (
                self.current_width // 2 - hint_text.get_width() // 2,
                self.current_height // 2 + 30,
            ),
        )

    def _draw_speed_selection_screen(self):
        self.snake_game.draw_background(
            self.win, self.current_width, self.current_height
        )

        display_name = self.user_name if self.user_name else "Player"
        prompt_text = big_font.render(
            f"Hello {display_name}! Choose Speed:", True, TEXT_COLOR
        )
        self.win.blit(
            prompt_text,
            (
                self.current_width // 2 - prompt_text.get_width() // 2,
                self.current_height // 2 - 120,
            ),
        )

        draw_button(
            self.win,
            self.easy_button_rect,
            "Easy",
            (0, 120, 0),
            font,
            TEXT_COLOR,
            hover_color=(0, 180, 0),
            border_color=BUTTON_BORDER_COLOR,
            is_selected=(self.game_speed_level == "Easy"),
            focused_rect=self.focused_rect,
        )
        draw_button(
            self.win,
            self.medium_button_rect,
            "Medium",
            (0, 80, 120),
            font,
            TEXT_COLOR,
            hover_color=(0, 120, 180),
            border_color=BUTTON_BORDER_COLOR,
            is_selected=(self.game_speed_level == "Medium"),
            focused_rect=self.focused_rect,
        )
        draw_button(
            self.win,
            self.hard_button_rect,
            "Hard",
            (120, 0, 0),
            font,
            TEXT_COLOR,
            hover_color=(180, 0, 0),
            border_color=BUTTON_BORDER_COLOR,
            is_selected=(self.game_speed_level == "Hard"),
            focused_rect=self.focused_rect,
        )
        draw_button(
            self.win,
            self.view_scores_button_rect,
            "View Score History",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            focused_rect=self.focused_rect,
        )
        draw_button(
            self.win,
            self.settings_button_rect,
            "Settings",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            focused_rect=self.focused_rect,
        )
        draw_button(
            self.win,
            self.quit_button_rect,
            "Quit Game",
            (150, 0, 0),
            font,
            TEXT_COLOR,
            hover_color=(200, 0, 0),
            border_color=BUTTON_BORDER_COLOR,
            focused_rect=self.focused_rect,
        )

    def _draw_game_over_screen(self):
        overlay = pygame.Surface(
            (self.current_width, self.current_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.win.blit(overlay, (0, 0))

        game_over_text = big_font.render("GAME OVER!", True, TEXT_COLOR)
        self.win.blit(
            game_over_text,
            (
                self.current_width // 2 - game_over_text.get_width() // 2,
                self.current_height // 2 - 100,
            ),
        )

        your_score_text = font.render(
            f"Your Score: {self.snake_game.score}", True, TEXT_COLOR
        )
        self.win.blit(
            your_score_text,
            (
                self.current_width // 2 - your_score_text.get_width() // 2,
                self.current_height // 2 - 40,
            ),
        )

        highest_score = self._get_highest_score_for_user_and_level(
            self.user_name, self.game_speed_level
        )
        highest_score_text = medium_font.render(
            f"Your Highest ({self.game_speed_level}): {highest_score}",
            True,
            ACCENT_COLOR,
        )
        self.win.blit(
            highest_score_text,
            (
                self.current_width // 2 - highest_score_text.get_width() // 2,
                self.current_height // 2,
            ),
        )

        draw_button(
            self.win,
            self.play_again_button_rect,
            "Play Again",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            focused_rect=self.focused_rect,
        )

    def _draw_score_history_screen(self):
        self.snake_game.draw_background(
            self.win, self.current_width, self.current_height
        )

        title_text = big_font.render("Score History", True, TEXT_COLOR)
        self.win.blit(
            title_text, (self.current_width // 2 - title_text.get_width() // 2, 50)
        )

        draw_button(
            self.win,
            self.easy_scores_tab_rect,
            "Easy",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            is_selected=(self.score_display_level == "Easy"),
            focused_rect=self.focused_rect,
        )
        draw_button(
            self.win,
            self.medium_scores_tab_rect,
            "Medium",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            is_selected=(self.score_display_level == "Medium"),
            focused_rect=self.focused_rect,
        )
        draw_button(
            self.win,
            self.hard_scores_tab_rect,
            "Hard",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            is_selected=(self.score_display_level == "Hard"),
            focused_rect=self.focused_rect,
        )

        top_scores = self._get_global_top_scores_for_level(self.score_display_level)

        if top_scores:
            y_offset = 180
            for i, score_entry in enumerate(top_scores):
                score_text = font.render(
                    f"{i + 1}. {score_entry['user']} - {score_entry['score']}",
                    True,
                    TEXT_COLOR,
                )
                self.win.blit(
                    score_text,
                    (self.current_width // 2 - score_text.get_width() // 2, y_offset),
                )
                y_offset += 40
        else:
            no_scores_text = font.render(
                "No scores for this level yet!", True, TEXT_COLOR
            )
            self.win.blit(
                no_scores_text,
                (self.current_width // 2 - no_scores_text.get_width() // 2, 250),
            )

        draw_button(
            self.win,
            self.back_button_rect,
            "Back",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            focused_rect=self.focused_rect,
        )

    def _draw_settings_screen(self):
        self.snake_game.draw_background(
            self.win, self.current_width, self.current_height
        )

        title_text = big_font.render("Settings", True, TEXT_COLOR)
        self.win.blit(
            title_text, (self.current_width // 2 - title_text.get_width() // 2, 50)
        )

        draw_input_box(
            self.win,
            self.settings_input_rect,
            self.input_box_text,
            self.input_active and self.focused_rect == self.settings_input_rect,
            font,
            TEXT_COLOR,
            self.focused_rect,
            prompt_text="Change Your Name:",
            default_display_text=self.user_name,
        )

        hint_text = smaller_font.render(
            "Press ENTER to save changes", True, (180, 180, 180)
        )
        self.win.blit(
            hint_text,
            (
                self.current_width // 2 - hint_text.get_width() // 2,
                self.settings_input_rect.y + self.settings_input_rect.height + 5,
            ),
        )

        draw_button(
            self.win,
            self.back_button_rect,
            "Back",
            BUTTON_DEFAULT_COLOR,
            font,
            TEXT_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            border_color=BUTTON_BORDER_COLOR,
            focused_rect=self.focused_rect,
        )

    def _draw_pause_button(self):
        if self.snake_game.paused:
            icon_color = ACCENT_COLOR
            pygame.draw.polygon(
                self.win,
                icon_color,
                [
                    (self.pause_button_rect.x + 15, self.pause_button_rect.y + 10),
                    (self.pause_button_rect.x + 15, self.pause_button_rect.y + 30),
                    (self.pause_button_rect.x + 30, self.pause_button_rect.y + 20),
                ],
            )
        else:
            icon_color = ACCENT_COLOR
            pygame.draw.rect(
                self.win,
                icon_color,
                (self.pause_button_rect.x + 12, self.pause_button_rect.y + 10, 5, 20),
            )
            pygame.draw.rect(
                self.win,
                icon_color,
                (self.pause_button_rect.x + 23, self.pause_button_rect.y + 10, 5, 20),
            )

        pygame.draw.rect(
            self.win, BUTTON_BORDER_COLOR, self.pause_button_rect, 2, border_radius=5
        )
