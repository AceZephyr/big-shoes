from constants import *

import pygame
import copy
import steplogic

CTRL = pygame.K_LCTRL | pygame.K_RCTRL

SHIFT = pygame.K_LSHIFT | pygame.K_RSHIFT

FLAGS = pygame.RESIZABLE

DEFAULT_SIZE = (1500, 400)

FONT = None

BACKGROUND_COLOR = (0, 0, 0)

GRAPH_BACKGROUND_COLOR_1 = (0, 0, 0)

GRAPH_BACKGROUND_COLOR_2 = (16, 16, 16)

BORDER_LINE_COLOR = (255, 255, 255)

GRIDLINE_COLOR = (32, 32, 32)

GRAPH_LABEL_COLOR = (255, 255, 255)

BATTLE_CHECK_COLOR = (0, 128, 128)

BATTLE_CHECK_PREEMPTIVE_COLOR = (196, 0, 196)

BATTLE_CHECK_SELECTED_OUTLINE_COLOR = (196, 196, 0)

LEFT_OFFSET = 36

BOTTOM_OFFSET = 18

START_STEP = Step(0, 0)

STEP_PER_GRIDLINE = 2

X_GRIDLINE_WIDTH = 12

X_GRIDLINES_PER_TEXT = 2

START_DANGER = 0

TOP_DANGER = 10000

MIN_TOP_DANGER = 100

MAX_TOP_DANGER = 65536

Y_GRIDLINE_HEIGHT = 12

DEFAULT_SCROLL_STEPS = STEP_PER_GRIDLINE

HOLD_SHIFT_SCROLL_STEPS = 10 * DEFAULT_SCROLL_STEPS

SELECTED_STEP = None


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


def x_coordinate_by_step(step: Step):
    pixel_dist_from_left = START_STEP.distance_to_step(step) * (X_GRIDLINE_WIDTH // STEP_PER_GRIDLINE)
    return pixel_dist_from_left + LEFT_OFFSET


def graph_height(surface):
    return surface.get_height() - BOTTOM_OFFSET


def y_coordinate_by_danger(surface, danger: int):
    g_height = graph_height(surface)
    return (g_height * (TOP_DANGER - danger)) // TOP_DANGER


def danger_by_y_coordinate(surface, y: int):
    g_height = graph_height(surface)
    return (TOP_DANGER * (g_height - y)) // g_height


running = True


def main():
    global SELECTED_STEP, running

    pygame.init()
    pygame.display.set_caption("Big Shoes")

    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)

    surface = pygame.display.set_mode(DEFAULT_SIZE, FLAGS)
    font = pygame.font.SysFont(FONT, 16)

    clock = pygame.time.Clock()

    update = True

    # main loop
    while running:

        # events
        for event in pygame.event.get():

            if event.type == pygame.VIDEORESIZE:
                update = True
                surface = pygame.display.set_mode((event.w, event.h), FLAGS)

            elif event.type == pygame.KEYDOWN:
                if SELECTED_STEP is not None:
                    if event.key == pygame.K_ESCAPE:
                        update = True
                        SELECTED_STEP = None
                    elif event.key == pygame.K_RIGHT:
                        update = True
                        SELECTED_STEP.advance_steps(1)
                        if (pygame.key.get_mods() & CTRL) != 0:
                            while steplogic.encounter_at_step(SELECTED_STEP)[0] > TOP_DANGER:
                                SELECTED_STEP.advance_steps(1)
                    elif event.key == pygame.K_LEFT:
                        update = True
                        SELECTED_STEP.advance_steps(-1)
                        if (pygame.key.get_mods() & CTRL) != 0:
                            while steplogic.encounter_at_step(SELECTED_STEP)[0] > TOP_DANGER:
                                SELECTED_STEP.advance_steps(-1)

            elif event.type == pygame.MOUSEWHEEL:
                update = True
                if (pygame.key.get_mods() & CTRL) != 0:  # scroll in and out
                    scale_top_danger(-event.y)
                elif (pygame.key.get_mods() & SHIFT) != 0:
                    scroll_starting_step_by(-event.y * HOLD_SHIFT_SCROLL_STEPS)
                else:  # scroll left and right
                    scroll_starting_step_by(-event.y * DEFAULT_SCROLL_STEPS)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in {1, 3}:
                    selected_step = step_nearest_x_coordinate(event.pos[0])
                    if selected_step is not None:
                        update = True
                        SELECTED_STEP = selected_step


            elif event.type == pygame.QUIT:
                running = False

        if update:

            # draw background
            surface.fill(BACKGROUND_COLOR)

            # draw graph background
            x = LEFT_OFFSET
            step = copy.copy(START_STEP)
            step.stepid %= 2
            height = graph_height(surface)
            while x <= surface.get_width():
                step.advance_steps(128)
                right_x = x_coordinate_by_step(step)
                color = GRAPH_BACKGROUND_COLOR_1 if step.offset % 2 == 1 else GRAPH_BACKGROUND_COLOR_2
                pygame.draw.rect(surface, color, ((x, 0), (right_x, height)))
                x = right_x

            # gridlines
            x = LEFT_OFFSET
            gridline = 0
            stepid = START_STEP.stepid
            while x < surface.get_width():
                pygame.draw.line(surface, GRIDLINE_COLOR, (x, 0), (x, surface.get_height() - BOTTOM_OFFSET), 1)
                if gridline % X_GRIDLINES_PER_TEXT == 0:
                    txt = font.render(str(stepid), False, GRAPH_LABEL_COLOR)
                    surface.blit(txt, (x - (txt.get_width() // 2), surface.get_height() - BOTTOM_OFFSET + 4))
                x += X_GRIDLINE_WIDTH
                stepid = (stepid + (STEP_PER_GRIDLINE * 2)) % 256
                gridline += 1

            y = graph_height(surface)
            while y > 0:
                pygame.draw.line(surface, GRIDLINE_COLOR, (LEFT_OFFSET, y), (surface.get_width(), y))
                txt = font.render(str(danger_by_y_coordinate(surface, y)), False, GRAPH_LABEL_COLOR)
                surface.blit(txt, (LEFT_OFFSET - txt.get_width() - 4, y - txt.get_height() // 2))
                y -= Y_GRIDLINE_HEIGHT

            # battle checks
            x = LEFT_OFFSET + (X_GRIDLINE_WIDTH // STEP_PER_GRIDLINE)
            step = copy.copy(START_STEP)
            step.advance_steps(1)
            while x < surface.get_width():
                step_data = steplogic.encounter_at_step(step)
                if step_data[0] < TOP_DANGER:
                    y = y_coordinate_by_danger(surface, step_data[0])
                    color = BATTLE_CHECK_PREEMPTIVE_COLOR if step_data[1] else BATTLE_CHECK_COLOR
                    if SELECTED_STEP is not None and step == SELECTED_STEP:
                        pygame.draw.line(surface, BATTLE_CHECK_SELECTED_OUTLINE_COLOR, (x, 0), (x, y + 1), 5)
                    pygame.draw.line(surface, color, (x, 0), (x, y), 3)

                x += (X_GRIDLINE_WIDTH // STEP_PER_GRIDLINE)
                step.advance_steps(1)

            # offset text
            txt = font.render(str(START_STEP.offset), False, (255, 255, 255))
            surface.blit(txt, (2, surface.get_height() - txt.get_height() - 2))

            # bottom border
            pygame.draw.line(surface, BORDER_LINE_COLOR, (LEFT_OFFSET, surface.get_height() - BOTTOM_OFFSET),
                             (surface.get_width(), surface.get_height() - BOTTOM_OFFSET), 2)

            # left border
            pygame.draw.line(surface, BORDER_LINE_COLOR, (LEFT_OFFSET, 0),
                             (LEFT_OFFSET, surface.get_height() - BOTTOM_OFFSET), 2)

            pygame.display.update()
            update = False
        clock.tick(30)
