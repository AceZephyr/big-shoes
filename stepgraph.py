import time

from constants import *

from enum import Enum, auto
import threading
import pygame
import copy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow

CTRL = pygame.K_LCTRL | pygame.K_RCTRL

SHIFT = pygame.K_LSHIFT | pygame.K_RSHIFT

# should this be moved? idk, it's fine here
FLAGS = pygame.RESIZABLE


class DisplayMode(Enum):
    DEFAULT = auto(),
    TRACK = auto()


class Stepgraph:

    def step_nearest_x_coordinate(self, x: int) -> Step:
        step_width = self.app.settings.X_GRIDLINE_WIDTH // self.app.settings.STEP_PER_GRIDLINE
        x += (step_width // 2) - self.app.settings.LEFT_OFFSET
        if x < 0:
            return None
        step = copy.copy(self.left_edge_step) + 1
        return step

    def x_coordinate_by_step(self, step: Step) -> int:
        pixel_dist_from_left = self.left_edge_step.distance_to_step(step) * (
                self.app.settings.X_GRIDLINE_WIDTH // self.app.settings.STEP_PER_GRIDLINE)
        return pixel_dist_from_left + self.app.settings.LEFT_OFFSET

    def graph_height(self) -> int:
        return self.surface.get_height() - self.app.settings.BOTTOM_OFFSET

    def y_coordinate_by_danger(self, danger: int) -> int:
        return (self.graph_height() * (self.top_danger - danger)) // self.top_danger

    def danger_by_y_coordinate(self, y: int) -> int:
        return (self.top_danger * (self.graph_height() - y)) // self.graph_height()

    def scroll_starting_step_by(self, steps):
        if self.display_mode == DisplayMode.DEFAULT:
            self.left_edge_step += steps
        elif self.display_mode == DisplayMode.TRACK:
            self.track_mode_left_offset += steps

    def set_step_scroll(self, step: Step):
        if self.display_mode == DisplayMode.DEFAULT:
            self.left_edge_step = step
        elif self.display_mode == DisplayMode.TRACK:
            self.track_mode_left_offset = 0  # TODO: update logic

    def reset_scroll(self):
        if self.display_mode == DisplayMode.TRACK:
            self.track_mode_left_offset = -self.app.settings.DEFAULT_TRACK_LEFT_OFFSET

    def scale_top_danger(self, y):
        if y > 0:
            self.top_danger = int(self.top_danger * (1.25 * abs(y)))
        elif y < 0:
            self.top_danger = int(self.top_danger * (0.8 * abs(y)))
        self.top_danger = max(self.app.settings.MIN_TOP_DANGER, self.top_danger)
        self.top_danger = min(self.app.settings.MAX_TOP_DANGER, self.top_danger)

    def select(self, coords) -> bool:
        # select step
        step = self.step_nearest_x_coordinate(coords[0])
        if self.y_coordinate_by_danger(step.encounter_threshold(
                self.app.current_step_state.lure_rate, self.app.current_step_state.preempt_rate)[0]) > coords[1]:
            self.selected_step = step
            return True
        self.deselect()
        return True

    def deselect(self):
        self.selected_step = None

    def main(self):
        pygame.init()
        pygame.display.set_caption("Big Shoes")

        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)

        self.surface = pygame.display.set_mode(self.app.settings.STEPGRAPH_DEFAULT_SIZE, FLAGS)
        font = pygame.font.SysFont(self.app.settings.STEPGRAPH_FONT, 16)

        clock = pygame.time.Clock()

        update = True
        self.running = True

        # main loop
        while self.running:

            # events
            for event in pygame.event.get():

                if event.type == pygame.VIDEORESIZE:
                    update = True
                    self.surface = pygame.display.set_mode((event.w, event.h), FLAGS)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        update = True
                        if (pygame.key.get_mods() & CTRL) != 0:
                            self.display_preemptive_battle_checks = not self.display_preemptive_battle_checks
                        else:
                            self.display_preemptive_stepids = not self.display_preemptive_stepids
                    elif event.key == pygame.K_m:
                        update = True
                        self.display_battle_marks = not self.display_battle_marks
                    elif event.key == pygame.K_x:
                        update = True
                        self.display_extrapolation = not self.display_extrapolation
                    elif event.key == pygame.K_r:
                        update = True
                        self.reset_scroll()
                    elif event.key == pygame.K_d:
                        update = True
                        self.top_danger = self.app.settings.DEFAULT_TOP_DANGER
                    elif self.selected_step is not None:
                        if event.key == pygame.K_ESCAPE:
                            update = True
                            self.deselect()
                        elif event.key == pygame.K_RIGHT:
                            update = True
                            self.selected_step += 1
                            if (pygame.key.get_mods() & CTRL) != 0:
                                while self.selected_step.encounter_threshold(
                                        self.app.current_step_state.lure_rate,
                                        self.app.current_step_state.preempt_rate)[0] > self.top_danger:
                                    self.selected_step += 1
                        elif event.key == pygame.K_LEFT:
                            update = True
                            self.selected_step -= 1
                            if (pygame.key.get_mods() & CTRL) != 0:
                                while self.selected_step.encounter_threshold(
                                        self.app.current_step_state.lure_rate,
                                        self.app.current_step_state.preempt_rate)[0] > self.top_danger:
                                    self.selected_step -= 1

                elif event.type == pygame.MOUSEWHEEL:
                    update = True
                    if (pygame.key.get_mods() & CTRL) != 0:  # scroll in and out
                        self.scale_top_danger(-event.y)
                    elif (pygame.key.get_mods() & SHIFT) != 0:
                        self.scroll_starting_step_by(
                            -event.y * self.app.settings.HOLD_SHIFT_SCROLL_MULTIPLIER * self.app.settings.SCROLL_STEPS)
                    else:  # scroll left and right
                        self.scroll_starting_step_by(-event.y * self.app.settings.SCROLL_STEPS)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_RIGHT:
                        if self.select(event.pos):
                            update = True

                elif event.type == pygame.QUIT:
                    self.running = False

            if self.local_update_count != self.update_requests:
                update = True
                self.local_update_count = self.update_requests

            if update:

                # update text
                if self.text_timeout is not None and time.time() > self.text_timeout:
                    self.text_timeout = None
                    self.text = ""

                # draw background
                self.surface.fill(self.app.settings.BACKGROUND_COLOR)

                # update starting step
                if self.display_mode == DisplayMode.TRACK:
                    self.left_edge_step = copy.copy(self.app.current_step_state.step)
                    self.left_edge_step -= -self.track_mode_left_offset

                # draw graph background
                x = self.app.settings.LEFT_OFFSET
                step = copy.copy(self.left_edge_step)
                step.step_id %= 2
                height = self.graph_height()
                while x <= self.surface.get_width():
                    step += 128
                    right_x = self.x_coordinate_by_step(step)
                    color = self.app.settings.GRAPH_BACKGROUND_COLOR_1 if step.offset % 2 == 1 \
                        else self.app.settings.GRAPH_BACKGROUND_COLOR_2
                    pygame.draw.rect(self.surface, color, ((x, 0), (right_x, height)))
                    x = right_x

                # gridlines
                x = self.app.settings.LEFT_OFFSET
                gridline = 0
                stepid = self.left_edge_step.step_id
                while x < self.surface.get_width():
                    pygame.draw.line(self.surface, self.app.settings.GRIDLINE_COLOR, (x, 0), (x, self.graph_height()),
                                     1)
                    if gridline % self.app.settings.X_GRIDLINES_PER_TEXT == 0:
                        txt = font.render(str(stepid), False, self.app.settings.GRAPH_LABEL_COLOR)
                        self.surface.blit(txt, (x - (txt.get_width() // 2), self.graph_height() + 4))
                    x += self.app.settings.X_GRIDLINE_WIDTH
                    stepid = (stepid + (self.app.settings.STEP_PER_GRIDLINE * 2)) % 256
                    gridline += 1
                y = self.graph_height()
                while y > 0:
                    pygame.draw.line(self.surface, self.app.settings.GRIDLINE_COLOR, (self.app.settings.LEFT_OFFSET, y),
                                     (self.surface.get_width(), y))
                    txt = font.render(str(self.danger_by_y_coordinate(y)), False,
                                      self.app.settings.GRAPH_LABEL_COLOR)
                    self.surface.blit(txt,
                                      (self.app.settings.LEFT_OFFSET - txt.get_width() - 4, y - txt.get_height() // 2))
                    y -= self.app.settings.Y_GRIDLINE_HEIGHT

                # preemptive gridlines
                if self.display_preemptive_stepids:
                    x = self.app.settings.LEFT_OFFSET + (
                            self.app.settings.X_GRIDLINE_WIDTH // self.app.settings.STEP_PER_GRIDLINE)
                    step = copy.copy(self.left_edge_step) + 1
                    while x < self.surface.get_width():
                        step_data = step.encounter_threshold(self.app.current_step_state.lure_rate,
                                                             self.app.current_step_state.preempt_rate)
                        if step_data[1]:
                            y = self.y_coordinate_by_danger(step_data[0])
                            pygame.draw.line(self.surface, self.app.settings.GRIDLINE_PREEMPTIVE_COLOR, (x, y),
                                             (x, self.graph_height()), 1)

                        x += (self.app.settings.X_GRIDLINE_WIDTH // self.app.settings.STEP_PER_GRIDLINE)
                        step += 1

                battle_marks = []
                # extrapolation lines
                if self.display_extrapolation and self.display_mode == DisplayMode.TRACK:
                    x = self.x_coordinate_by_step(self.app.current_step_state.step)
                    if x <= self.surface.get_width():
                        next_encounter_data = self.app.current_step_state.next_encounter_data()
                        for walking_steps in next_encounter_data:
                            x_start = self.x_coordinate_by_step(next_encounter_data[walking_steps][0][0])
                            y_start = self.y_coordinate_by_danger(next_encounter_data[walking_steps][0][1])
                            x_end = self.x_coordinate_by_step(next_encounter_data[walking_steps][1][0])
                            y_end = self.y_coordinate_by_danger(next_encounter_data[walking_steps][1][1])
                            color = self.app.settings.WALK_EXTRAPOLATION_COLOR if walking_steps == -1 \
                                else self.app.settings.RUN_EXTRAPOLATION_COLOR
                            pygame.draw.line(self.surface, color, (x_start, y_start), (x_end, y_end), width=3)
                            battle_marks.append((x_end, y_end))

                # battle checks
                x = self.app.settings.LEFT_OFFSET + (
                        self.app.settings.X_GRIDLINE_WIDTH // self.app.settings.STEP_PER_GRIDLINE)
                step = copy.copy(self.left_edge_step) + 1
                while x < self.surface.get_width():
                    step_data = step.encounter_threshold(self.app.current_step_state.lure_rate,
                                                         self.app.current_step_state.preempt_rate)
                    if step_data[0] < self.top_danger:
                        y = self.y_coordinate_by_danger(step_data[0])
                        color = self.app.settings.BATTLE_CHECK_PREEMPTIVE_COLOR if (
                                self.display_preemptive_battle_checks and step_data[1]
                        ) else self.app.settings.BATTLE_CHECK_COLOR
                        if self.selected_step is not None and step == self.selected_step:
                            pygame.draw.line(self.surface, self.app.settings.BATTLE_CHECK_SELECTED_OUTLINE_COLOR,
                                             (x, 0),
                                             (x, y + 1), 5)
                        pygame.draw.line(self.surface, color, (x, 0), (x, y), 3)

                    x += (self.app.settings.X_GRIDLINE_WIDTH // self.app.settings.STEP_PER_GRIDLINE)
                    step += 1

                # offset text
                txt = font.render(str(self.left_edge_step.offset), False, (255, 255, 255))
                self.surface.blit(txt, (2, self.surface.get_height() - txt.get_height() - 2))

                # bottom border
                pygame.draw.line(self.surface, self.app.settings.BORDER_LINE_COLOR,
                                 (self.app.settings.LEFT_OFFSET, self.graph_height()),
                                 (self.surface.get_width(), self.graph_height()), 2)

                # left border
                pygame.draw.line(self.surface, self.app.settings.BORDER_LINE_COLOR, (self.app.settings.LEFT_OFFSET, 0),
                                 (self.app.settings.LEFT_OFFSET, self.graph_height()), 2)

                # battle marks
                if self.display_battle_marks:
                    for mark in battle_marks:
                        pygame.draw.line(self.surface, self.app.settings.BATTLE_MARK_COLOR,
                                         (mark[0] - 5, mark[1] - 5), (mark[0] + 5, mark[1] + 5), width=3)
                        pygame.draw.line(self.surface, self.app.settings.BATTLE_MARK_COLOR,
                                         (mark[0] - 5, mark[1] + 5), (mark[0] + 5, mark[1] - 5), width=3)

                # current position dot
                if self.display_mode == DisplayMode.TRACK:
                    x = self.x_coordinate_by_step(self.app.current_step_state.step)
                    y = self.y_coordinate_by_danger(self.app.current_step_state.danger)
                    pygame.draw.rect(self.surface, self.app.settings.POSITION_MARK_COLOR, ((x - 3, y - 3), (7, 7)),
                                     width=0)

                # text
                # txt = font.render(self.text, False, (255, 255, 255))
                # self.surface.blit(txt, ())

                pygame.display.update()
                update = False
            clock.tick(30)
        pygame.quit()

    def start(self):
        if self.thread.is_alive():
            self.thread.join()
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def toggle(self):
        if not self.running:
            self.start()
        else:
            self.stop()

    def signal_update(self):
        self.update_requests += 1

    def __init__(self, app: "MainWindow"):
        self.app = app
        self.thread = threading.Thread(target=self.main)
        self.left_edge_step = Step(0, 0)

        self.selected_step = None
        self.top_danger = self.app.settings.DEFAULT_TOP_DANGER
        self.start_danger = 0
        self.display_mode = DisplayMode.DEFAULT
        self.running = False
        self.surface = None
        self.local_update_count = 0
        self.update_requests = 0
        self.track_mode_left_offset = -self.app.settings.DEFAULT_TRACK_LEFT_OFFSET
        self.text = ""
        self.text_timeout = 0

        self.display_preemptive_battle_checks = self.app.settings.DISPLAY_PREEMPTIVE_BATTLE_CHECKS_DEFAULT
        self.display_preemptive_stepids = self.app.settings.DISPLAY_PREEMPTIVE_STEPIDS_DEFAULT
        self.display_extrapolation = self.app.settings.DISPLAY_EXTRAPOLATION_DEFAULT
        self.display_battle_marks = self.app.settings.DISPLAY_BATTLE_MARKS_DEFAULT
