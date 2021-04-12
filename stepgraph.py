from constants import *
import settings

from enum import Enum, auto
import threading
import pygame
import copy

CTRL = pygame.K_LCTRL | pygame.K_RCTRL

SHIFT = pygame.K_LSHIFT | pygame.K_RSHIFT

# should this be moved? idk, it's fine here
FLAGS = pygame.RESIZABLE


class DisplayMode(Enum):
    DEFAULT = auto(),
    TRACK = auto()


class Stepgraph:

    def scroll_starting_step_by(self, steps):
        if self.display_mode == DisplayMode.DEFAULT:
            self.left_edge_step.advance_steps(steps)
        elif self.display_mode == DisplayMode.TRACK:
            self.track_mode_left_offset -= steps

    def scale_top_danger(self, y):
        if y > 0:
            self.top_danger = int(self.top_danger * (1.25 * abs(y)))
        elif y < 0:
            self.top_danger = int(self.top_danger * (0.8 * abs(y)))
        self.top_danger = max(self.settings.MIN_TOP_DANGER, self.top_danger)
        self.top_danger = min(self.settings.MAX_TOP_DANGER, self.top_danger)

    def step_nearest_x_coordinate(self, x: int):
        step_width = self.settings.X_GRIDLINE_WIDTH // self.settings.STEP_PER_GRIDLINE
        x += (step_width // 2) - self.settings.LEFT_OFFSET
        if x < 0:
            return None
        step = copy.copy(self.left_edge_step)
        step.advance_steps(x // step_width)
        return step

    def x_coordinate_by_step(self, step: Step):
        pixel_dist_from_left = self.left_edge_step.distance_to_step(step) * (
                self.settings.X_GRIDLINE_WIDTH // self.settings.STEP_PER_GRIDLINE)
        return pixel_dist_from_left + self.settings.LEFT_OFFSET

    def graph_height(self):
        return self.surface.get_height() - self.settings.BOTTOM_OFFSET

    def y_coordinate_by_danger(self, danger: int):
        return (self.graph_height() * (self.top_danger - danger)) // self.top_danger

    def danger_by_y_coordinate(self, y: int):
        return (self.top_danger * (self.graph_height() - y)) // self.graph_height()

    def main(self):
        pygame.init()
        pygame.display.set_caption("Big Shoes")

        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)

        self.surface = pygame.display.set_mode(self.settings.DEFAULT_SIZE, FLAGS)
        font = pygame.font.SysFont(self.settings.FONT, 16)

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
                    if self.selected_step is not None:
                        if event.key == pygame.K_ESCAPE:
                            update = True
                            self.selected_step = None
                        elif event.key == pygame.K_RIGHT:
                            update = True
                            self.selected_step.advance_steps(1)
                            if (pygame.key.get_mods() & CTRL) != 0:
                                while self.selected_step.encounter_threshold()[0] > self.top_danger:
                                    self.selected_step.advance_steps(1)
                        elif event.key == pygame.K_LEFT:
                            update = True
                            self.selected_step.advance_steps(-1)
                            if (pygame.key.get_mods() & CTRL) != 0:
                                while self.selected_step.encounter_threshold()[0] > self.top_danger:
                                    self.selected_step.advance_steps(-1)

                elif event.type == pygame.MOUSEWHEEL:
                    update = True
                    if (pygame.key.get_mods() & CTRL) != 0:  # scroll in and out
                        self.scale_top_danger(-event.y)
                    elif (pygame.key.get_mods() & SHIFT) != 0:
                        self.scroll_starting_step_by(
                            -event.y * self.settings.HOLD_SHIFT_SCROLL_MULTIPLIER * self.settings.SCROLL_STEPS)
                    else:  # scroll left and right
                        self.scroll_starting_step_by(-event.y * self.settings.SCROLL_STEPS)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in {1, 3}:
                        selected_step = self.step_nearest_x_coordinate(event.pos[0])
                        if selected_step is not None:
                            update = True
                            self.selected_step = selected_step


                elif event.type == pygame.QUIT:
                    self.running = False

            if self.local_update_count != self.update_requests:
                update = True
                self.local_update_count = self.update_requests

            if update:

                # draw background
                self.surface.fill(self.settings.BACKGROUND_COLOR)

                # update starting step
                if self.display_mode == DisplayMode.TRACK:
                    self.left_edge_step = copy.copy(self.current_step_state.step)
                    self.left_edge_step.advance_steps(-self.track_mode_left_offset)

                # draw graph background
                x = self.settings.LEFT_OFFSET
                step = copy.copy(self.left_edge_step)
                step.step_id %= 2
                height = self.graph_height()
                while x <= self.surface.get_width():
                    step.advance_steps(128)
                    right_x = self.x_coordinate_by_step(step)
                    color = self.settings.GRAPH_BACKGROUND_COLOR_1 if step.offset % 2 == 1 else self.settings.GRAPH_BACKGROUND_COLOR_2
                    pygame.draw.rect(self.surface, color, ((x, 0), (right_x, height)))
                    x = right_x

                # gridlines
                x = self.settings.LEFT_OFFSET
                gridline = 0
                stepid = self.left_edge_step.step_id
                while x < self.surface.get_width():
                    pygame.draw.line(self.surface, self.settings.GRIDLINE_COLOR, (x, 0), (x, self.graph_height()), 1)
                    if gridline % self.settings.X_GRIDLINES_PER_TEXT == 0:
                        txt = font.render(str(stepid), False, self.settings.GRAPH_LABEL_COLOR)
                        self.surface.blit(txt, (x - (txt.get_width() // 2), self.graph_height() + 4))
                    x += self.settings.X_GRIDLINE_WIDTH
                    stepid = (stepid + (self.settings.STEP_PER_GRIDLINE * 2)) % 256
                    gridline += 1

                y = self.graph_height()
                while y > 0:
                    pygame.draw.line(self.surface, self.settings.GRIDLINE_COLOR, (self.settings.LEFT_OFFSET, y),
                                     (self.surface.get_width(), y))
                    txt = font.render(str(self.danger_by_y_coordinate(y)), False,
                                      self.settings.GRAPH_LABEL_COLOR)
                    self.surface.blit(txt, (self.settings.LEFT_OFFSET - txt.get_width() - 4, y - txt.get_height() // 2))
                    y -= self.settings.Y_GRIDLINE_HEIGHT

                battle_marks = []

                # extrapolation lines
                if self.display_mode == DisplayMode.TRACK:
                    x = self.x_coordinate_by_step(self.current_step_state.step)
                    if x <= self.surface.get_width():
                        next_encounter_data = self.current_step_state.next_encounter_data()
                        for walking_steps in next_encounter_data:
                            x_start = self.x_coordinate_by_step(next_encounter_data[walking_steps][0][0])
                            y_start = self.y_coordinate_by_danger(next_encounter_data[walking_steps][0][1])
                            x_end = self.x_coordinate_by_step(next_encounter_data[walking_steps][1][0])
                            y_end = self.y_coordinate_by_danger(next_encounter_data[walking_steps][1][1])
                            color = self.settings.WALK_EXTRAPOLATION_COLOR if walking_steps == -1 else self.settings.RUN_EXTRAPOLATION_COLOR
                            pygame.draw.line(self.surface, color, (x_start, y_start), (x_end, y_end), width=3)
                            battle_marks.append((x_end, y_end))
                # battle checks
                x = self.settings.LEFT_OFFSET + (self.settings.X_GRIDLINE_WIDTH // self.settings.STEP_PER_GRIDLINE)
                step = copy.copy(self.left_edge_step)
                step.advance_steps(1)
                while x < self.surface.get_width():
                    step_data = step.encounter_threshold()
                    if step_data[0] < self.top_danger:
                        y = self.y_coordinate_by_danger(step_data[0])
                        color = self.settings.BATTLE_CHECK_PREEMPTIVE_COLOR if step_data[
                            1] else self.settings.BATTLE_CHECK_COLOR
                        if self.selected_step is not None and step == self.selected_step:
                            pygame.draw.line(self.surface, self.settings.BATTLE_CHECK_SELECTED_OUTLINE_COLOR, (x, 0),
                                             (x, y + 1), 5)
                        pygame.draw.line(self.surface, color, (x, 0), (x, y), 3)

                    x += (self.settings.X_GRIDLINE_WIDTH // self.settings.STEP_PER_GRIDLINE)
                    step.advance_steps(1)

                # offset text
                txt = font.render(str(self.left_edge_step.offset), False, (255, 255, 255))
                self.surface.blit(txt, (2, self.surface.get_height() - txt.get_height() - 2))

                # bottom border
                pygame.draw.line(self.surface, self.settings.BORDER_LINE_COLOR,
                                 (self.settings.LEFT_OFFSET, self.graph_height()),
                                 (self.surface.get_width(), self.graph_height()), 2)

                # left border
                pygame.draw.line(self.surface, self.settings.BORDER_LINE_COLOR, (self.settings.LEFT_OFFSET, 0),
                                 (self.settings.LEFT_OFFSET, self.graph_height()), 2)

                for mark in battle_marks:
                    pygame.draw.line(self.surface, self.settings.BATTLE_MARK_COLOR,
                                     (mark[0] - 5, mark[1] - 5), (mark[0] + 5, mark[1] + 5), width=3)
                    pygame.draw.line(self.surface, self.settings.BATTLE_MARK_COLOR,
                                     (mark[0] - 5, mark[1] + 5), (mark[0] + 5, mark[1] - 5), width=3)

                # current position dot
                if self.display_mode == DisplayMode.TRACK:
                    x = self.x_coordinate_by_step(self.current_step_state.step)
                    y = self.y_coordinate_by_danger(self.current_step_state.danger)
                    pygame.draw.rect(self.surface, (255, 0, 0), ((x - 3, y - 3), (7, 7)), width=0)

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

    def __init__(self, _settings: settings.Settings):
        self.settings = _settings
        self.thread = threading.Thread(target=self.main)
        self.left_edge_step = Step(0, 0)
        self.current_step_state: State = State(field_id=117, step=Step(0, 0), danger=0, step_fraction=0,
                                               formation_value=0)
        self.selected_step = None
        self.top_danger = 10000
        self.start_danger = 0
        self.display_mode = DisplayMode.DEFAULT
        self.running = False
        self.surface = None
        self.local_update_count = 0
        self.update_requests = 0
        self.track_mode_left_offset = self.settings.DEFAULT_TRACK_LEFT_OFFSET
