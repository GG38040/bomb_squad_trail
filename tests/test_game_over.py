import os
import pygame
from game import IEDMiniGame


def test_draw_game_over_screen_no_exception():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    game = IEDMiniGame(800, 600, points=42)
    game.game_over = True
    game.success = False
    try:
        game.draw_game_over_screen(screen)
    finally:
        pygame.quit()
