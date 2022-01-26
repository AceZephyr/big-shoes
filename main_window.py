import os
import re
import sys

import win32process
from dearpygui import dearpygui as dpg
from win32comext.shell import shell

import formation_extrapolator_new
import formation_list_new
import hook
import settings
import stepgraph_new
from watch_window import WatchWindow


def center(modal_id):
    viewport_width = dpg.get_viewport_client_width()
    viewport_height = dpg.get_viewport_client_height()

    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])


def show_error(title, message, selection_callback=None):
    def _callback(sender, unused, user_data):
        dpg.delete_item(user_data[0])
        if selection_callback is not None:
            selection_callback(user_data)

    with dpg.mutex():
        with dpg.window(label=title, modal=True, no_close=True) as modal_id:
            dpg.add_text(message)
            dpg.add_button(label="Ok", width=75, user_data=(modal_id, True), callback=_callback)

    center(modal_id)


class ConnectEmulatorDialog:
    def on_emulator_select(self):
        selected_emu = dpg.get_value(self.input_emu_name)
        pids = self.pids[selected_emu]
        dpg.configure_item(self.input_emu_pid, items=pids, default_value=pids[0])
        versions = [x.name for x in hook.Hook.EMULATOR_MAP[selected_emu][1]]
        dpg.configure_item(self.input_emu_ver, items=versions, default_value=versions[0])

    def click_connect(self):
        selected_emu = dpg.get_value(self.input_emu_name)
        selected_pid = dpg.get_value(self.input_emu_pid)
        selected_version = dpg.get_value(self.input_emu_ver)
        manual_address = dpg.get_value(self.input_manual_addr)

        for platform_version in hook.Hook.EMULATOR_MAP[selected_emu][1]:
            if platform_version.name == selected_version:

                if platform_version.version == "__MANUAL__":
                    if re.fullmatch("[0-9a-fA-F]+", manual_address):
                        self.parent_app.hook.manual_address = int(manual_address, 16)
                    else:
                        self.parent_app.hook.manual_address = None
                        show_error("Invalid manual offset",
                                   "Must input a valid address for a manual offset in Manual mode.")
                        return

                self.parent_app.hook.hooked_platform = platform_version
                self.parent_app.hook.hooked_process_id = int(selected_pid)
                self.parent_app.hook.start()
                dpg.delete_item(self.modal_id)

    def __init__(self, app, pids):
        self.parent_app = app
        self.pids = pids
        self.pid_names = sorted(list(self.pids.keys()), key=lambda x: x.lower())

        with dpg.mutex():
            with dpg.window(label="Connect to Emulator", modal=True, no_collapse=True, no_resize=True) as modal_id:
                self.modal_id = modal_id
                with dpg.group(width=200):
                    self.input_emu_name = dpg.add_combo(
                        label="Emulator Name", items=self.pid_names, default_value=self.pid_names[0],
                        callback=self.on_emulator_select)
                    self.input_emu_pid = dpg.add_combo(label="Emulator Process ID")
                    self.input_emu_ver = dpg.add_combo(label="Emulator Version")
                    self.input_manual_addr = dpg.add_input_text(label="Manual Address")
                    dpg.add_separator()
                    self.button_connect = dpg.add_button(user_data=(modal_id, 0), label="Connect",
                                                         callback=self.click_connect)
                    self.button_show_window = dpg.add_button(user_data=(modal_id, 1), label="Show this Window")
                    self.button_address_search = dpg.add_button(user_data=(modal_id, 2), label="Address Search")
        center(modal_id)
        self.on_emulator_select()


class MainWindow:

    def click_exit(self):
        self.hook.running = False
        self.running = False
        dpg.stop_dearpygui()

    def update_title(self, new_title):
        dpg.set_viewport_title(f"Big Shoes ({new_title})")

    def click_connect_to_emulator(self):
        if self.hook.is_running():
            show_error("Already Connected", "Already connected. Disconnect first.")
            return
        pids = hook.get_emu_process_ids()
        if len(pids) > 0:
            ConnectEmulatorDialog(self, pids)
        else:
            show_error("No Emulators Detected", "No emulators that can be connected to were detected.")

    def click_connect_to_pc(self):
        if self.hook.is_running():
            show_error("Already Connected", "Already connected. Disconnect first.")
            return
        pid = hook.get_pc_process_id()
        if pid is not None:
            self.hook.hooked_platform = hook.Hook.PC_PLATFORM
            self.hook.hooked_process_id = pid
            self.hook.start()
        else:
            show_error("FF7 PC Not Detected", "FF7 PC was not detected.")

    def click_disconnect(self):
        self.hook.stop()

    def click_watch_window(self):
        if dpg.is_item_shown(self.watch_window.window_id):
            dpg.hide_item(self.watch_window.window_id)
        else:
            dpg.show_item(self.watch_window.window_id)

    def click_stepgraph(self):
        if dpg.is_item_shown(self.stepgraph.window_id):
            dpg.hide_item(self.stepgraph.window_id)
        else:
            dpg.show_item(self.stepgraph.window_id)

    def click_fmext(self):
        if dpg.is_item_shown(self.formation_extrapolator.window_id):
            dpg.hide_item(self.formation_extrapolator.window_id)
        else:
            dpg.show_item(self.formation_extrapolator.window_id)

    def click_fmlist(self):
        if dpg.is_item_shown(self.formation_list.window_id):
            dpg.hide_item(self.formation_list.window_id)
        else:
            dpg.show_item(self.formation_list.window_id)

    def run(self):
        dpg.set_exit_callback(self.click_exit)

        dpg.create_viewport(title="Big Shoes", width=1200, height=800)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.primary_window, True)
        self.running = True

        self.watch_window.run()
        self.stepgraph.run()
        self.formation_extrapolator.run()
        self.formation_list.run()

        self.update_title(self.settings.DISCONNECTED_TEXT)

        dpg.start_dearpygui()

        self.click_exit()

    def __init__(self):
        self.running = False

        dpg.create_context()

        self.settings = settings.Settings()

        self.hook = hook.Hook(self)

        self.watch_window = WatchWindow(self)
        self.stepgraph = stepgraph_new.Stepgraph(self)
        self.formation_extrapolator = formation_extrapolator_new.FormationExtrapolatorWindow(self)
        self.formation_list = formation_list_new.FormationListWindow(self)

        with dpg.viewport_menu_bar() as menu_bar:
            self.menu_bar = menu_bar
            with dpg.menu(label="File") as file_menu:
                self.file_menu = file_menu
                dpg.add_menu_item(label="Exit", callback=self.click_exit)
            with dpg.menu(label="Connect") as connect_menu:
                self.connect_menu = connect_menu
                dpg.add_menu_item(label="Connect to Emulator", callback=self.click_connect_to_emulator)
                dpg.add_menu_item(label="Connect to PC", callback=self.click_connect_to_pc)
                dpg.add_separator()
                dpg.add_menu_item(label="Disconnect", callback=self.click_disconnect)
            with dpg.menu(label="Window") as window_menu:
                self.window_menu = window_menu
                dpg.add_menu_item(label="Watches", callback=self.click_watch_window)
                dpg.add_separator()
                dpg.add_menu_item(label="Stepgraph", callback=self.click_stepgraph)
                dpg.add_separator()
                dpg.add_menu_item(label="Formation Extrapolator", callback=self.click_fmext)
                dpg.add_menu_item(label="Formation List", callback=self.click_fmlist)
            with dpg.menu(label="Debug") as debug_menu:
                self.debug_menu = debug_menu
                dpg.add_menu_item(label="About", callback=dpg.show_about)
                dpg.add_menu_item(label="Debug", callback=dpg.show_debug)
                dpg.add_menu_item(label="Documentation", callback=dpg.show_documentation)
                dpg.add_menu_item(label="Font Manager", callback=dpg.show_font_manager)
                dpg.add_menu_item(label="Item Registry", callback=dpg.show_item_registry)
                dpg.add_menu_item(label="Metrics", callback=dpg.show_metrics)
                dpg.add_menu_item(label="Style Editor", callback=dpg.show_style_editor)

        self.primary_window = dpg.add_window()

        dpg.configure_app(docking=True)


if __name__ == '__main__':
    # if sys.argv[-1] == "try_admin":
    #     script = os.path.abspath(sys.argv[0])
    #     params = ' '.join([script] + sys.argv[1:-1])
    #     shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
    #     sys.exit(0)
    APP = MainWindow()
    try:
        sys.exit(APP.run())
    except KeyboardInterrupt as inter:
        print("stopping due to keyboard interrupt")
        APP.running = False
        sys.exit(-1)
