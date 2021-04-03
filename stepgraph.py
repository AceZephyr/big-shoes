import pygame

FLAGS = pygame.RESIZABLE

BACKGROUND_COLOR = (0, 0, 0)


def main():
    pygame.init()

    surface = pygame.display.set_mode((1500, 240), FLAGS)

    running = True

    # main loop
    while running:
        surface.fill(BACKGROUND_COLOR)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                surface = pygame.display.set_mode((event.w, event.h), FLAGS)
            if event.type == pygame.QUIT:
                running = False
