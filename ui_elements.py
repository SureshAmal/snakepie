import pygame
import time
from constants import (
    TEXT_COLOR,
    BUTTON_BORDER_COLOR,
    FOCUSED_BORDER_COLOR,
    INPUT_BOX_BG_COLOR,
    INPUT_BOX_BORDER_ACTIVE_COLOR,
    INPUT_BOX_BORDER_INACTIVE_COLOR,
)


def draw_button(
    surface,
    rect,
    text,
    default_color,
    font,
    text_color=TEXT_COLOR,
    hover_color=None,
    border_color=BUTTON_BORDER_COLOR,
    border_width=2,
    is_selected=False,
    focused_rect=None,
):
    current_color = default_color
    if rect.collidepoint(pygame.mouse.get_pos()):
        current_color = hover_color if hover_color else default_color

    pygame.draw.rect(surface, current_color, rect, border_radius=5)

    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=5)

    if is_selected:
        pygame.draw.rect(surface, TEXT_COLOR, rect, border_width + 1, border_radius=5)

    if focused_rect == rect:
        pygame.draw.rect(
            surface, FOCUSED_BORDER_COLOR, rect, border_width + 2, border_radius=5
        )

    text_surface = font.render(text, True, text_color)
    surface.blit(
        text_surface,
        (
            rect.x + (rect.width - text_surface.get_width()) // 2,
            rect.y + (rect.height - text_surface.get_height()) // 2,
        ),
    )


def draw_input_box(
    surface,
    rect,
    current_text_buffer,
    is_active,
    font,
    text_color,
    focused_rect=None,
    prompt_text="",
    default_display_text="",
    smaller_font=None,
):
    box_border_color = (
        INPUT_BOX_BORDER_ACTIVE_COLOR if is_active else INPUT_BOX_BORDER_INACTIVE_COLOR
    )

    pygame.draw.rect(surface, INPUT_BOX_BG_COLOR, rect, border_radius=5)
    pygame.draw.rect(surface, box_border_color, rect, 2, border_radius=5)

    if focused_rect == rect:
        pygame.draw.rect(surface, FOCUSED_BORDER_COLOR, rect, 2 + 2, border_radius=5)

    text_to_display = current_text_buffer if is_active else default_display_text
    display_text_surface = font.render(text_to_display, True, text_color)
    surface.blit(display_text_surface, (rect.x + 5, rect.y + 5))

    if is_active and int(time.time() * 2) % 2 == 0:
        cursor_pos = rect.x + 5 + display_text_surface.get_width()
        pygame.draw.line(
            surface,
            text_color,
            (cursor_pos, rect.y + 5),
            (cursor_pos, rect.y + rect.height - 5),
            2,
        )

    if prompt_text and smaller_font:
        prompt_surf = smaller_font.render(prompt_text, True, (180, 180, 180))
        prompt_text_x = rect.x
        prompt_text_y = rect.y - prompt_surf.get_height() - 5
        surface.blit(prompt_surf, (prompt_text_x, prompt_text_y))
