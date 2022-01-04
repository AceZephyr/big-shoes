import threading
import time

from dearpygui import dearpygui as dpg

import constants
import hook


class FormationListWindow:
    ADDR_FIELDID = hook.Address(0x9A05C, 0x8C15D0, 16, "Field ID")
    ADDR_SELTABLE = hook.Address(0x9AC30, 0x8C0DC4, 8, "Selected Table")

    def main(self):
        while self.parent_app.running:
            time.sleep(1 / 2)

            if not dpg.is_item_shown(self.window_id) or not self.parent_app.hook.is_running():
                continue

            field_id = self.parent_app.hook.read_key(self.field_key)

            if field_id not in constants.FIELDS:
                continue

            field = constants.FIELDS[field_id]

            table_id = self.parent_app.hook.read_key(self.table_key)

            table = field.table1 if field.table2 is None or table_id == 0 else field.table2

            encounters = []

            for enc_slot in table.standard:
                formation = enc_slot.formation
                if formation == 0:
                    break
                rate = enc_slot.rate
                enemy_names = [constants.ENEMY_DATA[en]["name"] for en in
                               constants.ENCOUNTER_DATA[formation].enemies]
                preemptable = "Yes" if constants.ENCOUNTER_DATA[formation].preemptable else "No"
                encounters.append((str(formation), "\n".join(enemy_names), str(rate),
                                   constants.ENCOUNTER_DATA[formation].encounter_type.label, preemptable))
            for enc_slot in table.special:
                formation = enc_slot.formation
                if formation == 0:
                    break
                rate = enc_slot.rate
                enemy_names = [constants.ENEMY_DATA[en]["name"] for en in
                               constants.ENCOUNTER_DATA[formation].enemies]
                preemptable = "---"
                encounters.append((str(formation), "\n".join(enemy_names), str(rate),
                                   constants.ENCOUNTER_DATA[formation].encounter_type.label, preemptable))
            for i in range(self.row_count):
                for j in range(len(self.cell_ids[i])):
                    if i < len(encounters):
                        dpg.set_value(self.cell_ids[i][j], encounters[i][j])
                    else:
                        dpg.set_value(self.cell_ids[i][j], "")

    def run(self):
        self.thread.start()

    def __init__(self, app):
        self.parent_app = app
        self.thread = threading.Thread(target=self.main)

        self.cell_ids = []

        self.row_count = 10
        with dpg.window(label="Formation List", width=800, show=False) as window_id:
            self.window_id = window_id
            with dpg.table(header_row=True, resizable=True):
                dpg.add_table_column(label="Formation ID")
                dpg.add_table_column(label="Enemies")
                dpg.add_table_column(label="Encounter Rate")
                dpg.add_table_column(label="Enemy Formation")
                dpg.add_table_column(label="Preemptable")

                for row_num in range(self.row_count):
                    with dpg.table_row():
                        self.cell_ids.append([dpg.add_text("") for _ in range(5)])

        self.field_key = app.hook.register_address(FormationListWindow.ADDR_FIELDID, 0)[0]
        self.table_key = app.hook.register_address(FormationListWindow.ADDR_SELTABLE, 0)[0]
