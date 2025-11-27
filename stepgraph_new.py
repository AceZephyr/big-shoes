import threading
import time
from enum import Enum, auto

from dearpygui import dearpygui as dpg

import constants
import hook
from main_window import center, show_error

WIDTH = 150
WIDTH_DIVISION = 4
MAX_WIDTH = 500

MAX_TOP_DANGER = 40000
MIN_TOP_DANGER = 500


def is_ctrl_down():
    return dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)


def is_alt_down():
    return dpg.is_key_down(dpg.mvKey_LAlt) or dpg.is_key_down(dpg.mvKey_RAlt)


def is_shift_down():
    return dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)


class DisplayMode(Enum):
    DEFAULT = auto(),
    TRACK = auto()


class SpecificStepDialog:
    def go(self):
        stepid = dpg.get_value(self.input_stepid)
        offset = dpg.get_value(self.input_offset)
        if not stepid.isnumeric() or not offset.isnumeric() or int(stepid) % 2 == 1:
            show_error("Invalid Input", "Not a valid step.")
            return
        destination_step = constants.Step(step_id=int(stepid), offset=int(offset))
        self.callback(destination_step)
        dpg.delete_item(self.modal_id)

    def __init__(self, callback):
        self.callback = callback

        with dpg.mutex():
            with dpg.window(label="Go To Specific Step", modal=True, no_collapse=True, no_resize=True) as modal_id:
                self.modal_id = modal_id
                with dpg.group(width=200):
                    self.input_stepid = dpg.add_input_text(label="Step ID")
                    self.input_offset = dpg.add_input_text(label="Offset")
                    dpg.add_separator()
                    self.button_go = dpg.add_button(label="Go", callback=lambda: self.go())
        center(modal_id)


class Stepgraph:
    ADDR_STEPID = hook.Address(0x9C540, 0x8C165C, 8, "Step ID")
    ADDR_OFFSET = hook.Address(0x9AD2C, 0x8C1660, 8, "Offset")
    ADDR_FRAC = hook.Address(0x9C6D8, 0x8C1664, 8, "Step Fraction")
    ADDR_DANGER = hook.Address(0x7173C, 0x8C1668, 16, "Danger")
    ADDR_FMACCUM = hook.Address(0x71C20, 0x8C1650, 8, "Formation Accumulator")
    ADDR_FIELDID = hook.Address(0x9A05C, 0x8C15D0, 16, "Field ID")
    ADDR_SELTABLE = hook.Address(0x9AC30, 0x8C0DC4, 8, "Selected Table")
    ADDR_DDM = hook.Address(0x9AC04, 0x8C0D98, 16, "Danger Divisor Multiplier")
    ADDR_LURE = hook.Address(0x62F19, 0x9BCAD9, 8, "Lure Rate")
    ADDR_PREEMPT = hook.Address(0x62F1B, 0x9BCADB, 8, "Preempt Rate")
    ADDR_LASTENC = hook.Address(0x7E774, 0x8C1654, 16, "Last Encounter Formation")

    def update_axes(self):
        dpg.set_axis_limits(self.x_axis, 0, self.width)
        dpg.set_axis_limits(self.y_axis, 0, self.top_danger)

    def _mouse_wheel_handler(self, sender, scroll_amount):
        with dpg.mutex():
            if dpg.is_item_hovered(self.window_id):
                if is_ctrl_down():
                    if is_shift_down():
                        self.top_danger -= scroll_amount * 5000
                    else:
                        self.top_danger -= scroll_amount * 500
                elif is_alt_down():
                    if is_shift_down():
                        self.width -= scroll_amount * 20
                    else:
                        self.width -= scroll_amount * 2
                elif is_shift_down():
                    self.track_mode_left_offset += scroll_amount * 40
                else:
                    self.track_mode_left_offset += scroll_amount * 4
                if self.top_danger < MIN_TOP_DANGER:
                    self.top_danger = MIN_TOP_DANGER
                elif self.top_danger > MAX_TOP_DANGER:
                    self.top_danger = MAX_TOP_DANGER
                if self.width < 10:
                    self.width = 10
                elif self.width > MAX_WIDTH:
                    self.width = MAX_WIDTH

    def _window_resize_handler(self):
        # TODO: where tf do these numbers 16 and 54 come from and how can i calculate these based on the current layout?
        dpg.set_item_width(self.plot_id, dpg.get_item_width(self.window_id) - 16)
        dpg.set_item_height(self.plot_id, dpg.get_item_height(self.window_id) - 54)

    def goto_current_position(self):
        self.track_mode_left_offset = self.parent_app.settings.DEFAULT_TRACK_LEFT_OFFSET

    def specific_step_callback(self, step):
        self.track_mode_left_offset = self.step_state.step - step

    def click_goto_specific_step(self):
        SpecificStepDialog(callback=lambda: self.specific_step_callback())

    def main(self):
        def _r(_orig_val, k):
            new_value = self.parent_app.hook.read_key(k)
            self.update = self.update or new_value != _orig_val
            return new_value

        def _v(_orig_val, k):
            new_value = dpg.get_value(k)
            self.update = self.update or new_value != _orig_val
            return new_value

        def _(_orig_val, _new_val):
            self.update = self.update or _new_val != _orig_val
            return _new_val

        while True:
            with self.parent_app.running_lock:
                if not self.parent_app.running:
                    return

            time.sleep(1 / 15)

            if not dpg.is_item_shown(self.window_id):
                continue

            self.update = False

            self.step_state.step.step_id = _r(self.step_state.step.step_id, self.stepid_key)
            self.step_state.step.offset = _r(self.step_state.step.offset, self.offset_key)
            self.step_state.step_fraction = _r(self.step_state.step_fraction, self.frac_key)
            self.step_state.danger = _r(self.step_state.danger, self.danger_key)
            self.step_state.formation_value = _r(self.step_state.formation_value, self.fmaccum_key)
            new_field_id = _r(self.step_state.field_id, self.fieldid_key)
            if new_field_id in constants.FIELDS:
                self.step_state.field_id = new_field_id
            self.step_state.table_index = _r(self.step_state.table_index, self.seltable_key)
            self.step_state.danger_divisor_multiplier = _r(self.step_state.danger_divisor_multiplier, self.ddm_key)
            self.step_state.lure_rate = _r(self.step_state.lure_rate, self.lure_key)
            self.step_state.preempt_rate = _r(self.step_state.preempt_rate, self.preempt_key)
            self.step_state.last_encounter_formation = _r(self.step_state.last_encounter_formation, self.lastenc_key)

            self.left_edge_step = _(self.left_edge_step, self.step_state.step - self.track_mode_left_offset)

            self.stored_width = _(self.stored_width, self.width)
            self.stored_top_danger = _(self.stored_top_danger, self.top_danger)

            self.stored_encounter_thresholds = _v(self.stored_encounter_thresholds, self.menu_encounter_thresholds)

            self.stored_encounter_marks = _v(self.stored_encounter_marks, self.menu_encounter_marks)

            self.stored_underwalk_labels = _v(self.stored_underwalk_labels, self.menu_underwalk_labels)

            self.stored_offset_labels = _v(self.stored_offset_labels, self.menu_offset_labels)

            self.stored_preempt_gridlines = _v(self.stored_preempt_gridlines, self.menu_preempt_gridlines)
            self.stored_preemt_encounter_thresholds = _v(self.stored_preemt_encounter_thresholds,
                                                         self.menu_preempt_encounter_thresholds)
            self.stored_walk_danger_projection_lines = _v(self.stored_walk_danger_projection_lines,
                                                          self.menu_walk_danger_projection_lines)
            self.stored_run_danger_projection_lines = _v(self.stored_run_danger_projection_lines,
                                                         self.menu_run_danger_projection_lines)
            self.stored_run_initial_danger_projection_line = _v(self.stored_run_initial_danger_projection_line,
                                                                self.menu_run_initial_danger_projection_line)

            self.stored_current_position = _v(self.stored_current_position, self.menu_current_position)

            if not self.update:
                continue

            self.update_axes()

            for line_id in self.plot_elements:
                dpg.delete_item(line_id)
            self.plot_elements.clear()

            connected = self.parent_app.hook.hooked_process_id is not None

            # axis ticks
            dpg.set_axis_ticks(self.x_axis, tuple(
                [(str((self.left_edge_step + x).step_id), x) for x in
                 range((WIDTH_DIVISION - (self.left_edge_step.step_id // 2 % WIDTH_DIVISION)) % WIDTH_DIVISION,
                       self.width, WIDTH_DIVISION)]))

            # preemptive gridlines
            if self.stored_preempt_gridlines:
                for x in range(0, self.width):
                    step_data = (self.left_edge_step + x).encounter_threshold(self.step_state.lure_rate,
                                                                              self.step_state.preempt_rate)
                    if step_data[1]:
                        self.plot_elements.append(
                            dpg.draw_line((x, self.top_danger), (x, 0), thickness=0.05, parent=self.plot_id,
                                          color=self.parent_app.settings.GRIDLINE_PREEMPTIVE_COLOR))

            if self.stored_encounter_thresholds:
                for x in range(0, self.width):
                    step_data = (self.left_edge_step + x).encounter_threshold(self.step_state.lure_rate,
                                                                              self.step_state.preempt_rate)
                    # battle checks
                    if step_data[0] < self.top_danger:
                        y = step_data[0]
                        color = (
                            self.parent_app.settings.BATTLE_CHECK_PREEMPTIVE_COLOR
                            if step_data[1] and self.stored_preemt_encounter_thresholds
                            else self.parent_app.settings.BATTLE_CHECK_COLOR
                        )
                        self.plot_elements.append(
                            dpg.draw_line((x, self.top_danger), (x, y), thickness=0.25, parent=self.plot_id,
                                          color=color))

            if connected and self.step_state.table() is not None:
                next_encounter_data = self.step_state.next_encounter_data()
                i = 0
                for walking_steps in next_encounter_data:
                    color = (
                        self.parent_app.settings.WALK_EXTRAPOLATION_COLOR
                        if walking_steps == -1
                        else self.parent_app.settings.RUN_EXTRAPOLATION_COLOR
                    )
                    x_start = next_encounter_data[walking_steps][0][0] - self.left_edge_step
                    y_start = next_encounter_data[walking_steps][0][1]
                    x_end = next_encounter_data[walking_steps][1][0] - self.left_edge_step
                    y_end = next_encounter_data[walking_steps][1][1]
                    if x_start > 10000:
                        x_start -= 32768
                    if x_end > 10000:
                        x_end -= 32768
                    if (walking_steps == -1 and self.stored_walk_danger_projection_lines) or (
                            walking_steps != -1 and self.stored_run_danger_projection_lines) or (
                            walking_steps == 0 and self.stored_run_initial_danger_projection_line):
                        self.plot_elements.append(dpg.draw_line(
                            (x_start, y_start), (x_end, y_end), thickness=0.25, color=color, parent=self.plot_id))
                        if self.stored_encounter_marks:
                            self.plot_elements.append(dpg.draw_circle((x_end, y_end), parent=self.plot_id, radius=0.5,
                                                                      fill=self.parent_app.settings.BATTLE_MARK_COLOR))
                    i += 1
                if self.stored_underwalk_labels:
                    sorted_keys = sorted(set(next_encounter_data.keys()))
                    for i in range(1, len(sorted_keys) - 1):
                        walking_steps = sorted_keys[i]
                        next_walking_steps = sorted_keys[i + 1]
                        x_end = next_encounter_data[walking_steps][1][0] - self.left_edge_step
                        y_end = next_encounter_data[walking_steps][1][1]
                        self.plot_elements.append(dpg.draw_text(
                            (x_end + 1, y_end), str(next_walking_steps - walking_steps), size=2.5,
                            parent=self.plot_id))

                if self.stored_offset_labels:
                    offset = self.left_edge_step.offset
                    height = (self.top_danger / self.width) * 10
                    for i in range(-self.left_edge_step.step_id // 2, self.width, 128):
                        self.plot_elements.append(
                            dpg.draw_text((max(1, i), height), str(offset), size=2, parent=self.plot_id))
                        offset = (offset + 13) % 256

            # draw point
            if self.stored_current_position:
                x = self.track_mode_left_offset
                y = self.step_state.danger
                self.plot_elements.append(dpg.draw_circle((x, y), parent=self.plot_id, radius=0.5,
                                                          fill=self.parent_app.settings.POSITION_MARK_COLOR))

    def run(self):
        self.thread.start()

    def __init__(self, app):
        self.parent_app = app

        self.plot_elements = []

        self.top_danger = app.settings.DEFAULT_TOP_DANGER
        self.start_danger = 0
        self.display_mode = DisplayMode.DEFAULT
        self.track_mode_left_offset = app.settings.DEFAULT_TRACK_LEFT_OFFSET
        self.left_edge_step = constants.Step(0, 0)
        self.width = WIDTH
        self.stored_width = 0
        self.stored_top_danger = 0

        with dpg.handler_registry():
            dpg.add_mouse_wheel_handler(
                callback=lambda sender, scroll_amount: self._mouse_wheel_handler(sender, scroll_amount))

        with dpg.window(label="Stepgraph", width=1000, show=False, no_scrollbar=True) as window_id:
            self.window_id = window_id

            with dpg.item_handler_registry(tag="widget handler") as window_handler:
                dpg.add_item_resize_handler(callback=lambda: self._window_resize_handler())
            dpg.bind_item_handler_registry(window_id, window_handler)

            with dpg.plot(width=1000, no_mouse_pos=True, no_box_select=True, no_child=True,
                          no_menus=True, tracked=False) as plot_id:
                self.plot_id = plot_id

                self.x_axis = dpg.add_plot_axis(dpg.mvXAxis)
                self.y_axis = dpg.add_plot_axis(dpg.mvYAxis)

                self.update_axes()

            with dpg.menu_bar() as menu_bar:
                self.menu_bar_id = menu_bar
                with dpg.menu(label="View") as view_menu:
                    self.view_menu_id = view_menu

                    self.menu_encounter_thresholds = dpg.add_menu_item(
                        label="Encounter Thresholds", check=True, default_value=True)
                    self.stored_encounter_thresholds = dpg.get_value(self.menu_encounter_thresholds)

                    self.menu_encounter_marks = dpg.add_menu_item(
                        label="Encounter Marks", check=True, default_value=True)
                    self.stored_encounter_marks = dpg.get_value(self.menu_encounter_marks)

                    self.menu_walk_danger_projection_lines = dpg.add_menu_item(
                        label="Walk Danger Projection Lines", check=True, default_value=True)
                    self.stored_walk_danger_projection_lines = dpg.get_value(self.menu_walk_danger_projection_lines)

                    self.menu_run_danger_projection_lines = dpg.add_menu_item(
                        label="Run Danger Projection Lines", check=True, default_value=True)
                    self.stored_run_danger_projection_lines = dpg.get_value(self.menu_run_danger_projection_lines)

                    self.menu_run_initial_danger_projection_line = dpg.add_menu_item(
                        label="Run Initial Projection Line", check=True, default_value=True)
                    self.stored_run_initial_danger_projection_line = dpg.get_value(
                        self.menu_run_initial_danger_projection_line)

                    self.menu_current_position = dpg.add_menu_item(
                        label="Current Position", check=True, default_value=True)
                    self.stored_current_position = dpg.get_value(self.menu_current_position)

                    dpg.add_separator()

                    self.menu_underwalk_labels = dpg.add_menu_item(
                        label="Underwalk Labels", check=True, default_value=True)
                    self.stored_underwalk_labels = dpg.get_value(self.menu_underwalk_labels)

                    self.menu_offset_labels = dpg.add_menu_item(
                        label="Offset Labels", check=True, default_value=True)
                    self.stored_offset_labels = dpg.get_value(self.menu_offset_labels)

                    dpg.add_separator()

                    self.menu_preempt_gridlines = dpg.add_menu_item(
                        label="Preemptive Gridlines", check=True, default_value=True)
                    self.stored_preempt_gridlines = dpg.get_value(self.menu_preempt_gridlines)

                    self.menu_preempt_encounter_thresholds = dpg.add_menu_item(
                        label="Preemptive Encounter Thresholds", check=True, default_value=True)
                    self.stored_preemt_encounter_thresholds = dpg.get_value(self.menu_preempt_encounter_thresholds)

                with dpg.menu(label="Go To") as goto_menu:
                    self.goto_menu_id = goto_menu

                    self.menu_goto_current_position = dpg.add_menu_item(
                        label="Current Position", callback=lambda: self.goto_current_position()
                    )

                    self.menu_goto_step = dpg.add_menu_item(
                        label="Specific Step", callback=lambda: self.click_goto_specific_step()
                    )

        dpg.set_axis_ticks(self.x_axis, tuple([("", x) for x in range(MAX_WIDTH + 1000)]))

        self.step_state = constants.State(field_id=116, step=constants.Step(0, 0))

        self.stepid_key, self.step_state.step.step_id = app.hook.register_address(Stepgraph.ADDR_STEPID, 0)
        self.offset_key, self.step_state.step.offset = app.hook.register_address(Stepgraph.ADDR_OFFSET, 0)
        self.frac_key, self.step_state.step_fraction = app.hook.register_address(Stepgraph.ADDR_FRAC, 0)
        self.danger_key, self.step_state.danger = app.hook.register_address(Stepgraph.ADDR_DANGER, 0)
        self.fmaccum_key, self.step_state.formation_value = app.hook.register_address(Stepgraph.ADDR_FMACCUM, 0)
        self.fieldid_key, self.step_state.field_id = app.hook.register_address(Stepgraph.ADDR_FIELDID, 116)
        self.seltable_key, self.step_state.table_index = app.hook.register_address(Stepgraph.ADDR_SELTABLE, 0)
        self.ddm_key, self.step_state.danger_divisor_multiplier = app.hook.register_address(Stepgraph.ADDR_DDM, 0)
        self.lure_key, self.step_state.lure_rate = app.hook.register_address(Stepgraph.ADDR_LURE, 0)
        self.preempt_key, self.step_state.preempt_rate = app.hook.register_address(Stepgraph.ADDR_PREEMPT, 0)
        self.lastenc_key, self.step_state.last_encounter_formation = app.hook.register_address(Stepgraph.ADDR_LASTENC,
                                                                                               0)

        self.update = False
        self.thread = threading.Thread(target=self.main)
