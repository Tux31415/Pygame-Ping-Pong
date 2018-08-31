import pygame
import math
import random

from constants import *
from ping_pong import PingPong


def main():
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    game = PingPong()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.QUIT:
                 running = False

        # Time in seconds since the last call of tick
        delta = clock.tick(FRAMERATE) / 1000

        game.update(delta)
        screen.fill(BACKGROUND_COLOR)
        game.render(screen)

        # Update the window
        pygame.display.flip()

if __name__ == "__main__":
    main()
