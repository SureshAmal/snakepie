import pygame
import random
from constants import (
    SNAKE_COLOR,
    HEAD_COLOR,
    FOOD_COLOR,
    BG_COLOR_START,
    BG_COLOR_END,
    TEXT_COLOR,
    font,
    big_font,
)


class SnakeGame:
    def __init__(self, width, height):
        self.snake = [(200, 200), (220, 200), (240, 200)]
        self.direction = "RIGHT"
        self.food = self._set_new_food(width, height)
        self.score = 0
        self.paused = False
        self.game_over = False
        self.width = width
        self.height = height

    def _set_new_food(self, width, height):
        while True:
            food = (
                random.randint(0, (width // 20) - 1) * 20,
                random.randint(0, (height // 20) - 1) * 20,
            )
            if food not in self.snake:
                return food

    def draw_background(self, surface, width, height):
        for y in range(height):
            ratio = y / height
            color_r = int(
                BG_COLOR_START[0] + (BG_COLOR_END[0] - BG_COLOR_START[0]) * ratio
            )
            color_g = int(
                BG_COLOR_START[1] + (BG_COLOR_END[1] - BG_COLOR_START[1]) * ratio
            )
            color_b = int(
                BG_COLOR_START[2] + (BG_COLOR_END[2] - BG_COLOR_START[2]) * ratio
            )
            color = (color_r, color_g, color_b)
            pygame.draw.line(surface, color, (0, y), (width, y))

    def draw(self, surface, width, height):
        self.draw_background(surface, width, height)
        if not self.game_over:
            for i, (x, y) in enumerate(self.snake):
                if i == len(self.snake) - 1:
                    pygame.draw.rect(surface, HEAD_COLOR, (x, y, 20, 20))
                else:
                    pygame.draw.rect(surface, SNAKE_COLOR, (x, y, 20, 20))
            pygame.draw.rect(surface, FOOD_COLOR, (self.food[0], self.food[1], 20, 20))

            score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
            surface.blit(score_text, (10, 10))

            if self.paused:
                paused_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                paused_overlay.fill((0, 0, 0, 150))
                surface.blit(paused_overlay, (0, 0))
                paused_text = big_font.render("PAUSED", True, TEXT_COLOR)
                surface.blit(
                    paused_text,
                    (
                        width // 2 - paused_text.get_width() // 2,
                        height // 2 - paused_text.get_height() // 2,
                    ),
                )

    def update(self):
        if not self.paused and not self.game_over:
            head = self.snake[-1]
            new_head = head

            if self.direction == "RIGHT":
                new_head = (head[0] + 20, head[1])
            elif self.direction == "LEFT":
                new_head = (head[0] - 20, head[1])
            elif self.direction == "UP":
                new_head = (head[0], head[1] - 20)
            elif self.direction == "DOWN":
                new_head = (head[0], head[1] + 20)

            self.snake.append(new_head)

            if self.food == new_head:
                self.food = self._set_new_food(self.width, self.height)
                self.score += 1
            else:
                self.snake.pop(0)

            if (
                new_head[0] < 0
                or new_head[0] >= self.width
                or new_head[1] < 0
                or new_head[1] >= self.height
                or new_head in self.snake[:-1]
            ):
                self.game_over = True
        return self.game_over

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_UP
                or event.key == pygame.K_w
                or event.key == pygame.K_k
            ) and self.direction != "DOWN":
                self.direction = "UP"
            elif (
                event.key == pygame.K_DOWN
                or event.key == pygame.K_s
                or event.key == pygame.K_j
            ) and self.direction != "UP":
                self.direction = "DOWN"
            elif (
                event.key == pygame.K_LEFT
                or event.key == pygame.K_a
                or event.key == pygame.K_h
            ) and self.direction != "RIGHT":
                self.direction = "LEFT"
            elif (
                event.key == pygame.K_RIGHT
                or event.key == pygame.K_d
                or event.key == pygame.K_l
            ) and self.direction != "LEFT":
                self.direction = "RIGHT"

    def reset(self, width, height):
        self.width = width
        self.height = height
        self.snake = [(200, 200), (220, 200), (240, 200)]
        self.direction = "RIGHT"
        self.food = self._set_new_food(width, height)
        self.score = 0
        self.paused = False
        self.game_over = False

    def update_dimensions(self, width, height):
        self.width = width
        self.height = height
