import threading
import time

from dearpygui import dearpygui as dpg

import constants
import hook


class FormationExtrapolatorWindow:
    ADDR_FMACCUM = hook.Address(0x71C20, 0x8C1650, 8, "Formation Accumulator")
    ADDR_FIELDID = hook.Address(0x9A05C, 0x8C15D0, 16, "Field ID")
    ADDR_SELTABLE = hook.Address(0x9AC30, 0x8C0DC4, 8, "Selected Table")
    ADDR_PREEMPT = hook.Address(0x62F1B, 0x9BCADB, 8, "Preempt Rate")
    ADDR_LASTENC = hook.Address(0x7E774, 0x8C1654, 16, "Last Encounter Formation")

    def main(self):
        while self.parent_app.running:

            time.sleep(1 / 2)

            if not dpg.is_item_shown(self.window_id) or not self.parent_app.hook.is_running():
                continue

            field_id = self.parent_app.hook.read_key(self.field_key)

            if field_id not in constants.FIELDS:
                continue

            preempt_rate = self.parent_app.hook.read_key(self.preempt_key)
            table = self.parent_app.hook.read_key(self.table_key)
            old_fmaccum = self.parent_app.hook.read_key(self.fmaccum_key)
            last_formation = self.parent_app.hook.read_key(self.lastenc_key)

            for i in range(self.row_count):
                formation_data = constants.FIELDS[field_id].encounter_on_formation(
                    formation=old_fmaccum, preempt_rate=preempt_rate, table=table)
                formation_type = formation_data[2]
                if formation_type == "Normal":
                    if formation_data[0] == last_formation:
                        formation = formation_data[1]
                        new_fmaccum = old_fmaccum + 3
                    else:
                        formation = formation_data[0]
                        new_fmaccum = old_fmaccum + 2
                    preemptable = "Yes" if constants.ENCOUNTER_DATA[formation].preemptable == 1 else "No"
                else:
                    formation = formation_data[0]
                    new_fmaccum = old_fmaccum + 1
                    preemptable = "---"
                enemy_names = [constants.ENEMY_DATA[en]["name"] for en in
                               constants.ENCOUNTER_DATA[formation].enemies]

                dpg.set_value(self.cell_ids[i][0], str(old_fmaccum) + " -> " + str(new_fmaccum))
                dpg.set_value(self.cell_ids[i][1], str(formation))
                dpg.set_value(self.cell_ids[i][2], "\n".join(enemy_names))
                dpg.set_value(self.cell_ids[i][3], formation_type)
                dpg.set_value(self.cell_ids[i][4], preemptable)

                old_fmaccum = new_fmaccum
                last_formation = formation

    def run(self):
        self.thread.start()

    def __init__(self, app):
        self.parent_app = app
        self.thread = threading.Thread(target=self.main)

        self.cell_ids = []

        self.row_count = 10
        with dpg.window(label="Formation Extrapolator", width=800, show=False) as window_id:
            self.window_id = window_id
            with dpg.table(header_row=True, resizable=True):
                dpg.add_table_column(label="Formation Accumulator")
                dpg.add_table_column(label="Formation ID")
                dpg.add_table_column(label="Enemies")
                dpg.add_table_column(label="Enemy Formation")
                dpg.add_table_column(label="Preemptable")

                for row_num in range(self.row_count):
                    with dpg.table_row():
                        self.cell_ids.append([dpg.add_text("") for _ in range(5)])

        self.field_key = app.hook.register_address(FormationExtrapolatorWindow.ADDR_FIELDID, 0)[0]
        self.preempt_key = app.hook.register_address(FormationExtrapolatorWindow.ADDR_PREEMPT, 0)[0]
        self.table_key = app.hook.register_address(FormationExtrapolatorWindow.ADDR_SELTABLE, 0)[0]
        self.fmaccum_key = app.hook.register_address(FormationExtrapolatorWindow.ADDR_FMACCUM, 0)[0]
        self.lastenc_key = app.hook.register_address(FormationExtrapolatorWindow.ADDR_LASTENC, 0)[0]
