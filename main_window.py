import formation_list
from constants import *
import settings

import tkinter as tk
from tkinter import ttk, messagebox
import stepgraph
import hook
import win32gui
import win32process
import formation_extrapolator


class DisplayTable(tk.LabelFrame):
    def __init__(self, master):
        tk.LabelFrame.__init__(self, master, borderwidth=1, text="Values", relief=tk.SOLID)
        self.data = []

    def add_row(self, name: str):
        namevar = tk.StringVar(value=name)
        valvar = tk.IntVar(value=0)
        tk.Label(self, textvariable=namevar, anchor="e", width=20).grid(row=len(self.data), column=0)
        tk.Label(self, textvariable=valvar, anchor="w", width=8).grid(row=len(self.data), column=1)
        self.data.append([namevar, valvar])

    def set_row_value(self, row: int, value: int):
        self.data[row][1].set(value=value)


class Application(tk.Frame):

    def open_formation_extrapolator(self):
        self.formation_extrapolator_windows.append(formation_extrapolator.FormationExtrapolator(self))

    def open_formation_list(self):
        self.formation_list_windows.append(formation_list.FormationList(self))

    def update_formation_windows(self):
        for window in self.formation_extrapolator_windows:
            window.update_display()

    def disconnect(self):
        self.hook.stop()

    def connect_pc(self):
        if self.hook.running:
            messagebox.showinfo("Already Connected", "Already connected. Disconnect first.")
            return
        pid = hook.get_pc_process_id()
        if pid is None:
            messagebox.showinfo("FF7 PC Not Detected", "FF7 PC was not detected.")
            return
        self.hook.hooked_platform = hook.Hook.PC_PLATFORM
        self.hook.hooked_process_id = pid
        self.hook.start()

    def connect_emulator(self):
        if self.hook.running:
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
            version_select['values'] = [x.name for x in hook.Hook.EMULATOR_MAP[emu_select_out.get()]]
            version_select.current(0)

        def on_process_select(index, value, op):
            pass

        tk.Label(emu_connect_window, text="Emulator process name:").grid(row=0, column=0)

        emu_select_out.trace("w", on_emu_select)
        emu_select['values'] = sorted(list(pids.keys()), key=lambda x: x.lower())
        emu_select.grid(row=1, column=0)
        emu_select.current(0)

        tk.Label(emu_connect_window, text="Emulator process id:").grid(row=0, column=1)

        process_select_out.trace("w", on_process_select)
        process_select['values'] = sorted(list(pids[emu_select_out.get()]))
        process_select.grid(row=1, column=1)
        process_select.current(0)

        tk.Label(emu_connect_window, text="Emulator version:").grid(row=0, column=2)

        version_select['values'] = [x.name for x in hook.Hook.EMULATOR_MAP[emu_select_out.get()]]
        version_select.grid(row=1, column=2)
        version_select.current(0)

        def show_window_button():
            def _callback(hwnd, pid):
                thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
                if process_id == pid:
                    win32gui.BringWindowToTop(hwnd)

            win32gui.EnumWindows(_callback, int(process_select_out.get()))

        tk.Button(emu_connect_window, text="Show This Window", command=show_window_button).grid(row=2, column=1)

        def connect_button(_app: "Application"):
            for platform_version in hook.Hook.EMULATOR_MAP[emu_select_out.get()]:
                if platform_version.name == version_select_out.get():
                    _app.hook.hooked_platform = platform_version
                    _app.hook.hooked_process_id = int(process_select_out.get())
                    emu_connect_window.destroy()
                    _app.hook.start()

        tk.Button(emu_connect_window, text="Connect", command=lambda: connect_button(self)).grid(row=3, column=0,
                                                                                                 columnspan=4)

        emu_connect_window.mainloop()

    def on_close(self):
        self.stepgraph.stop()
        self.disconnect()
        try:
            self.master.destroy()
        except Exception:
            pass

    def __init__(self, _settings: settings.Settings, master=None):
        tk.Frame.__init__(self, master)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.settings = _settings

        self.stepgraph = stepgraph.Stepgraph(self)

        self.hook = hook.Hook(self)

        self.current_step_state: State = State(field_id=117, step=Step(0, 0), danger=0, step_fraction=0,
                                               formation_value=0)

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

        menu_window = tk.Menu(menubar, tearoff=0)
        menu_window.add_command(label="Toggle Stepgraph", command=self.stepgraph.toggle)
        menu_window.add_command(label="Open Formation Extrapolator", command=self.open_formation_extrapolator)
        menu_window.add_command(label="Open Formation List", command=self.open_formation_list)

        menubar.add_cascade(label="File", menu=menu_file)
        menubar.add_cascade(label="Connect", menu=menu_connect)
        menubar.add_cascade(label="Window", menu=menu_window)

        self.master.config(menu=menubar)

        self.connected_text = tk.StringVar(value="Disconnected.")
        tk.Label(textvariable=self.connected_text, anchor=tk.N, width=20).grid(row=1, column=0)

        memory_view = DisplayTable(self)
        memory_view.grid(row=0, column=0)
        memory_view.add_row("Step ID")
        memory_view.add_row("Step Fraction")
        memory_view.add_row("Offset")
        memory_view.add_row("Danger")
        memory_view.add_row("Formation Accumulator")
        memory_view.add_row("Field ID")
        memory_view.add_row("Table Index")
        memory_view.add_row("Danger Divisor Multiplier")
        memory_view.add_row("Lure Rate")
        memory_view.add_row("Preempt Rate")
        memory_view.add_row("Last Encounter Formation")
        self.memory_view = memory_view

        self.formation_extrapolator_windows = []
        self.formation_list_windows = []


if __name__ == '__main__':
    app = Application(settings.Settings())

    app.mainloop()

    app.on_close()
