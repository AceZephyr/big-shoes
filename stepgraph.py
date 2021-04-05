from constants import *

import pygame
import copy
import steplogic

FLAGS = pygame.RESIZABLE

DEFAULT_SIZE = (1500, 400)

FONT = None

BACKGROUND_COLOR = (0, 0, 0)

BORDER_LINE_COLOR = (255, 255, 255)

GRIDLINE_COLOR = (24, 24, 24)

BATTLE_CHECK_COLOR = (0, 128, 128)

BATTLE_CHECK_PREEMPTIVE_COLOR = (196, 0, 196)

LEFT_OFFSET = 36

BOTTOM_OFFSET = 18

START_STEP = Step(0, 0)

STEP_PER_GRIDLINE = 1

X_GRIDLINE_WIDTH = 12

X_GRIDLINES_PER_TEXT = 2

START_DANGER = 0

TOP_DANGER = 10000

MIN_TOP_DANGER = 100

MAX_TOP_DANGER = 65536

Y_GRIDLINE_HEIGHT = 12

DEFAULT_SCROLL_STEPS = 1

HOLD_SHIFT_SCROLL_STEPS = 10


def scroll_starting_step_by(steps):
    START_STEP.advance_steps(steps)


def scale_top_danger(y):
    global TOP_DANGER
    if y > 0:
        TOP_DANGER = int(TOP_DANGER * (1.25 * abs(y)))
    elif y < 0:
        TOP_DANGER = int(TOP_DANGER * (0.8 * abs(y)))
    TOP_DANGER = max(MIN_TOP_DANGER, TOP_DANGER)
    TOP_DANGER = min(MAX_TOP_DANGER, TOP_DANGER)


def step_nearest_x_coordinate(x: int):
    step_width = X_GRIDLINE_WIDTH // STEP_PER_GRIDLINE
    x += (step_width // 2) - LEFT_OFFSET
    if x < 0:
        return None
    step = copy.copy(START_STEP)
    step.advance_steps(x // step_width)
    return step


def x_coordinate_by_step(surface, step: Step):
    return


def graph_height(surface):
    return surface.get_height() - BOTTOM_OFFSET


def y_coordinate_by_danger(surface, danger: int):
    g_height = graph_height(surface)
    return (g_height * (TOP_DANGER - danger)) // TOP_DANGER


def danger_by_y_coordinate(surface, y: int):
    g_height = graph_height(surface)
    return (TOP_DANGER * (g_height - y)) // g_height


def main():
    pygame.init()
    pygame.display.set_caption("Big Shoes")

    surface = pygame.display.set_mode(DEFAULT_SIZE, FLAGS)
    font = pygame.font.SysFont(FONT, 16)

    clock = pygame.time.Clock()

    running = True

    # main loop
    while running:

        # events
        for event in pygame.event.get():

            if event.type == pygame.VIDEORESIZE:
                surface = pygame.display.set_mode((event.w, event.h), FLAGS)

            elif event.type == pygame.MOUSEWHEEL:
                if (pygame.key.get_mods() & (pygame.K_LCTRL | pygame.K_RCTRL)) != 0:  # scroll in and out
                    scale_top_danger(-event.y * DEFAULT_SCROLL_STEPS)
                elif (pygame.key.get_mods() & (pygame.K_LSHIFT | pygame.K_RSHIFT)) != 0:
                    scroll_starting_step_by(-event.y * HOLD_SHIFT_SCROLL_STEPS)
                else:  # scroll left and right
                    scroll_starting_step_by(-event.y * DEFAULT_SCROLL_STEPS)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in {1, 3}:
                    step = step_nearest_x_coordinate(event.pos[0])
                    if step is not None:
                        encdata = steplogic.encounter_at_step(step)
                        ycbd = y_coordinate_by_danger(surface, encdata[0])
                        print(step, encdata, ycbd, event)

            elif event.type == pygame.QUIT:
                running = False

        # draw background
        surface.fill(BACKGROUND_COLOR)

        # gridlines
        x = LEFT_OFFSET
        gridline = 0
        stepid = START_STEP.stepid
        while x < surface.get_width():
            pygame.draw.line(surface, GRIDLINE_COLOR, (x, 0), (x, surface.get_height() - BOTTOM_OFFSET), 1)
            if gridline % X_GRIDLINES_PER_TEXT == 0:
                txt = font.render(str(stepid), False, (255, 255, 255))
                surface.blit(txt, (x - (txt.get_width() // 2), surface.get_height() - BOTTOM_OFFSET + 4))
            x += X_GRIDLINE_WIDTH
            stepid = (stepid + (STEP_PER_GRIDLINE * 2)) % 256
            gridline += 1

        y = graph_height(surface)
        while y > 0:
            pygame.draw.line(surface, GRIDLINE_COLOR, (LEFT_OFFSET, y), (surface.get_width(), y))
            txt = font.render(str(danger_by_y_coordinate(surface, y)), False, (255, 255, 255))
            surface.blit(txt, (LEFT_OFFSET - txt.get_width() - 4, y - txt.get_height() // 2))
            y -= Y_GRIDLINE_HEIGHT

        # battle checks
        x = LEFT_OFFSET + X_GRIDLINE_WIDTH
        step = copy.copy(START_STEP)
        while x < surface.get_width():
            step_data = steplogic.encounter_at_step(step)
            if step_data[0] < TOP_DANGER:
                y = y_coordinate_by_danger(surface, step_data[0])
                pygame.draw.line(surface, BATTLE_CHECK_COLOR, (x, 0), (x, y), 3)
            x += (X_GRIDLINE_WIDTH // STEP_PER_GRIDLINE)
            step.advance_steps(1)

        # bottom border
        pygame.draw.line(surface, BORDER_LINE_COLOR, (LEFT_OFFSET, surface.get_height() - BOTTOM_OFFSET),
                         (surface.get_width(), surface.get_height() - BOTTOM_OFFSET), 2)

        # left border
        pygame.draw.line(surface, BORDER_LINE_COLOR, (LEFT_OFFSET, 0),
                         (LEFT_OFFSET, surface.get_height() - BOTTOM_OFFSET), 2)

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
