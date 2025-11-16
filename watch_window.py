import threading
import time

from dearpygui import dearpygui as dpg

import hook


class WatchWindow:
    ADDRESSES = [
        (hook.Address(0x9C540, 0x8C165C, 8, "Step ID"), str),
        (hook.Address(0x9AD2C, 0x8C1660, 8, "Offset"), str),
        (hook.Address(0x9C6D8, 0x8C1664, 8, "Step Fraction"), lambda x: str(x >> 5)),
        (hook.Address(0x7173C, 0x8C1668, 16, "Danger"), str),
        (hook.Address(0x71C20, 0x8C1650, 8, "Formation Accumulator"), str),
        (hook.Address(0x9A05C, 0x8C15D0, 16, "Field ID"), str),
        (hook.Address(0x9AC30, 0x8C0DC4, 8, "Selected Table"), str),
        (hook.Address(0x9AC04, 0x8C0D98, 16, "Danger Divisor Multiplier"), str),
        (hook.Address(0x62F19, 0x9BCAD9, 8, "Lure Rate"), str),
        (hook.Address(0x62F1B, 0x9BCADB, 8, "Preempt Rate"), str),
        (hook.Address(0x7E774, 0x8C1654, 16, "Last Encounter Formation"), str)
    ]

    def main(self):
        while self.parent_app.running:
            time.sleep(1 / 30)
            for i in range(len(self.address_keys)):
                self.address_values[i] = self.parent_app.hook.read_key(self.address_keys[i])
            with dpg.mutex():
                for i in range(len(self.table_ids)):
                    dpg.set_value(self.table_ids[i], self.watch_functions[i](self.address_values[i]))

    def run(self):
        self.thread.start()

    def __init__(self, app):
        self.parent_app = app
        self.thread = threading.Thread(target=self.main)
        print("ww: window")
        with dpg.window(label="Watches", width=400, show=False) as window_id:
            self.window_id = window_id
            print("ww table")
            with dpg.table(header_row=True, resizable=True):
                dpg.add_table_column(label="Address")
                self.table_ids = []
                self.address_keys = []
                self.address_values = []
                self.watch_functions = []
                for addr, func in WatchWindow.ADDRESSES:
                    with dpg.table_row():
                        print(f"address: {addr.name}")
                        dpg.add_text(addr.name)
                        k, v = app.hook.register_address(addr, 0)
                        self.address_keys.append(k)
                        self.address_values.append(v)
                        self.watch_functions.append(func)
                        self.table_ids.append(dpg.add_text(""))
                dpg.add_table_column(label="Value")
