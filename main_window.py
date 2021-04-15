import constants
import settings

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import stepgraph
import hook
import win32gui
import win32process
import win32security
import time


class DisplayTable(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.data = []

    def add_row(self, name: str):
        namevar = tk.StringVar(value=name)
        valvar = tk.IntVar(value=0)
        ttk.Label(self, textvariable=namevar).grid(row=len(self.data), column=0)
        ttk.Label(self, textvariable=valvar).grid(row=len(self.data), column=1)
        self.data.append([namevar, valvar])

    def set_row_value(self, row: int, value: int):
        self.data[row][1].set(value=value)


def adjust_privilege(name, attr=win32security.SE_PRIVILEGE_ENABLED):
    if isinstance(name, str):
        state = (win32security.LookupPrivilegeValue(None, name), attr)
    else:
        state = name
    hToken = win32security.OpenProcessToken(win32process.GetCurrentProcess(),
                                            win32security.TOKEN_ALL_ACCESS)
    return win32security.AdjustTokenPrivileges(hToken, False, [state])


class Application(ttk.Frame):

    def read(self, size: int, address: hook.Address):
        return self.hooked_platform.read_int(self.hooked_process_handle, address, size)

    def hook_main(self):
        hook._BASE_ADDRESS_CACHE = None
        adjust_privilege(win32security.SE_DEBUG_NAME)
        # hook into platform
        self.hooked_process_handle = hook.OpenProcess(0x1F0FFF, False, self.hooked_process_id)

        self.connected_text.set("Connected to " + self.hooked_platform.name)

        self.stepgraph.display_mode = stepgraph.DisplayMode.TRACK

        self.hook_running = True

        last_update_time = time.time() - 1
        while self.hook_running:
            try:
                # update display
                new_stepid = self.read(8, hook.Address.STEP_ID)
                new_step_fraction = self.read(8, hook.Address.STEP_FRACTION) // 32
                new_offset = self.read(8, hook.Address.OFFSET)
                new_danger = self.read(16, hook.Address.DANGER)
                new_fmaccum = self.read(8, hook.Address.FORMATION_ACCUMULATOR)
                new_field_id = self.read(16, hook.Address.FIELD_ID)
                new_selected_table = self.read(8, hook.Address.SELECTED_TABLE) + 1
                new_danger_divisor_multiplier = self.read(16, hook.Address.DANGER_DIVISOR_MULTIPLIER)
                new_lure_rate = self.read(8, hook.Address.LURE_RATE)
                new_preempt_rate = self.read(8, hook.Address.PREEMPT_RATE)

                update = False
                force_update = time.time() - last_update_time > 1

                if force_update or new_stepid != self.stepgraph.current_step_state.step.step_id:
                    update = True
                    app.memory_view.set_row_value(0, new_stepid)
                    self.stepgraph.current_step_state.step.step_id = new_stepid
                if force_update or new_step_fraction != self.stepgraph.current_step_state.step_fraction:
                    # update = True  # stepgraph doesn't care about fraction
                    app.memory_view.set_row_value(1, new_step_fraction)
                    self.stepgraph.current_step_state.step_fraction = new_step_fraction
                if force_update or new_offset != self.stepgraph.current_step_state.step.offset:
                    update = True
                    app.memory_view.set_row_value(2, new_offset)
                    self.stepgraph.current_step_state.step.offset = new_offset
                if force_update or new_danger != self.stepgraph.current_step_state.danger:
                    update = True
                    app.memory_view.set_row_value(3, new_danger)
                    self.stepgraph.current_step_state.danger = new_danger
                if force_update or new_fmaccum != self.stepgraph.current_step_state.formation_value:
                    update = True
                    app.memory_view.set_row_value(4, new_fmaccum)
                    self.stepgraph.current_step_state.formation_value = new_fmaccum
                if force_update or new_field_id != self.stepgraph.current_step_state.field_id:
                    field_id = new_field_id
                    if field_id in constants.FIELDS:
                        update = True
                        app.memory_view.set_row_value(5, new_field_id)
                        self.stepgraph.current_step_state.field_id = field_id
                if force_update or new_selected_table != self.stepgraph.current_step_state.table_index:
                    update = True
                    app.memory_view.set_row_value(6, new_selected_table)
                    self.stepgraph.current_step_state.table_index = new_selected_table
                if force_update or new_danger_divisor_multiplier != self.stepgraph.current_step_state.danger_divisor_multipler:
                    update = True
                    app.memory_view.set_row_value(7, new_danger_divisor_multiplier)
                    self.stepgraph.current_step_state.danger_divisor_multipler = new_danger_divisor_multiplier
                if force_update or new_lure_rate != self.stepgraph.current_step_state.lure_rate:
                    update = True
                    app.memory_view.set_row_value(8, new_lure_rate)
                    self.stepgraph.current_step_state.lure_rate = new_lure_rate
                if force_update or new_preempt_rate != self.stepgraph.current_step_state.preempt_rate:
                    update = True
                    app.memory_view.set_row_value(9, new_preempt_rate)
                    self.stepgraph.current_step_state.preempt_rate = new_preempt_rate

                if update:
                    self.stepgraph.update()
                    last_update_time = time.time()

            except Exception as e:
                if e is RuntimeError:
                    hook.running = False
                if str(type(e)) == '<class \'pywintypes.error\'>':
                    if e.args[0] == 299:  # process was closed probably
                        self.hook_running = False
                        break
            time.sleep(1 / self.settings.UPDATES_PER_SECOND)
        hook.CloseHandle(self.hooked_process_handle)
        self.hooked_process_handle = None
        self.hooked_process_id = None
        self.hooked_platform = None

        self.stepgraph.display_mode = stepgraph.DisplayMode.DEFAULT

        self.connected_text.set("Disconnected.")

        self.stepgraph.update()

    def disconnect(self):
        self.hook_running = False

    def connect_pc(self):
        if self.hook_running:
            messagebox.showinfo("Already Connected", "Already connected. Disconnect first.")
            return
        pid = hook.get_pc_process_id()
        if pid is None:
            messagebox.showinfo("FF7 PC Not Detected", "FF7 PC was not detected.")
            return
        self.hooked_platform = hook.PC_PLATFORM
        self.hooked_process_id = pid
        self.hook_thread = threading.Thread(target=self.hook_main)
        self.hook_thread.start()

    def connect_emulator(self):
        if self.hook_running:
            messagebox.showinfo("Already Connected", "Already connected. Disconnect first.")
            return
        pids = hook.get_emu_process_ids()
        if len(pids) == 0:
            messagebox.showinfo("No Emulators Detected", "No emulators that can be connected to were detected.")
            return
        emu_connect_window = tk.Toplevel(app)
        emu_connect_window.grid()
        emu_connect_window.geometry('650x250')

        emu_select_out = tk.StringVar()
        emu_select = ttk.Combobox(emu_connect_window, textvariable=emu_select_out, state="readonly", width=30)
        process_select_out = tk.StringVar()
        process_select = ttk.Combobox(emu_connect_window, textvariable=process_select_out, state="readonly", width=30)
        version_select_out = tk.StringVar()
        version_select = ttk.Combobox(emu_connect_window, textvariable=version_select_out, state="readonly", width=30)

        def on_emu_select(index, value, op):
            process_select['values'] = sorted(list(pids[emu_select_out.get()]))
            process_select.current(0)
            version_select['values'] = [x.name for x in hook.EMULATOR_MAP[emu_select_out.get()]]
            version_select.current(0)

        def on_process_select(index, value, op):
            pass

        ttk.Label(emu_connect_window, text="Emulator process name:").grid(row=0, column=0)

        emu_select_out.trace("w", on_emu_select)
        emu_select['values'] = sorted(list(pids.keys()), key=lambda x: x.lower())
        emu_select.grid(row=1, column=0)
        emu_select.current(0)

        ttk.Label(emu_connect_window, text="Emulator process id:").grid(row=0, column=1)

        process_select_out.trace("w", on_process_select)
        process_select['values'] = sorted(list(pids[emu_select_out.get()]))
        process_select.grid(row=1, column=1)
        process_select.current(0)

        ttk.Label(emu_connect_window, text="Emulator version:").grid(row=0, column=2)

        version_select['values'] = [x.name for x in hook.EMULATOR_MAP[emu_select_out.get()]]
        version_select.grid(row=1, column=2)
        version_select.current(0)

        def show_window_button():
            def _callback(hwnd, pid):
                thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
                if process_id == pid:
                    win32gui.BringWindowToTop(hwnd)

            win32gui.EnumWindows(_callback, int(process_select_out.get()))

        ttk.Button(emu_connect_window, text="Show This Window", command=show_window_button).grid(row=2, column=1)

        def connect_button(_app: "Application"):
            for platform_version in hook.EMULATOR_MAP[emu_select_out.get()]:
                if platform_version.name == version_select_out.get():
                    _app.hooked_platform = platform_version
                    _app.hooked_process_id = int(process_select_out.get())
                    emu_connect_window.destroy()
                    _app.hook_thread = threading.Thread(target=self.hook_main)
                    _app.hook_thread.start()

        ttk.Button(emu_connect_window, text="Connect", command=lambda: connect_button(self)).grid(row=3, column=0,
                                                                                                  columnspan=4)

        emu_connect_window.mainloop()

    def on_close(self):
        self.stepgraph.stop()
        self.disconnect()
        try:
            self.master.destroy()
        except Exception:
            pass

    def __init__(self, _settings, master=None):
        ttk.Frame.__init__(self, master)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.settings = _settings

        self.stepgraph = stepgraph.Stepgraph(_settings)

        self.hook_thread = threading.Thread(target=self.hook_main)
        self.hook_running = False

        self.hooked_platform = None
        self.hooked_process_id = None
        self.hooked_process_handle = None

        self.master.title("Big Shoes")
        self.master.iconphoto(True, tk.PhotoImage(file="icon.png"))
        self.master.geometry('500x500')
        self.grid()

        menubar = tk.Menu(self)

        menu_file = tk.Menu(menubar, tearoff=0)
        menu_file.add_command(label="Exit", command=self.quit)

        menu_connect = tk.Menu(menubar, tearoff=0)
        menu_connect.add_command(label="Connect to Emulator", command=self.connect_emulator)
        menu_connect.add_command(label="Connect to PC", command=self.connect_pc)
        menu_connect.add_separator()
        menu_connect.add_command(label="Disconnect", command=self.disconnect)

        menubar.add_cascade(label="File", menu=menu_file)
        menubar.add_cascade(label="Connect", menu=menu_connect)

        self.master.config(menu=menubar)

        self.connected_text = tk.StringVar(value="Disconnected.")
        ttk.Label(textvariable=self.connected_text).grid(row=0, column=2)

        memory_view = DisplayTable(self)
        memory_view.grid(row=0, column=1)
        memory_view.add_row("Step ID")
        memory_view.add_row("Step Fraction")
        memory_view.add_row("Offset")
        memory_view.add_row("Danger")
        memory_view.add_row("Formation Accumulator")
        memory_view.add_row("Field ID")
        memory_view.add_row("Table Index")
        memory_view.add_row("DDM")
        memory_view.add_row("Lure Rate")
        memory_view.add_row("Preempt Rate")
        self.memory_view = memory_view

        ttk.Button(self, text="Toggle Stepgraph", command=self.stepgraph.toggle).grid(row=0, column=0)


if __name__ == '__main__':
    app = Application(settings.Settings())

    app.mainloop()

    app.on_close()
