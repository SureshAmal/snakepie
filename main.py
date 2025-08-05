import pygame
from game_manager import GameManager
from constants import WIDTH, HEIGHT


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    game_manager = GameManager(win)

    while True:
        game_manager.handle_events()
        game_manager.update()
        game_manager.draw()
        clock.tick(game_manager.game_speed_fps)


if __name__ == "__main__":
    main()
