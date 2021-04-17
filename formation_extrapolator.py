import constants
import formations

import tkinter as tk
from tkinter import ttk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import Application


class ExtrapolationTable(tk.Frame):

    def update_display_table(self):
        field = self.app.current_step_state.field()
        preempt_rate = self.app.current_step_state.preempt_rate
        table = self.app.current_step_state.table_index
        old_fmaccum = self.app.current_step_state.formation_value
        last_formation = self.app.current_step_state.last_encounter_formation
        for i in range(10):
            formation_data = formations.encounter_on_formation(field=field, formation=old_fmaccum,
                                                               preempt_rate=preempt_rate, table=table)
            formation_type = formation_data[2]
            if formation_type == "Normal":
                if formation_data[0] == last_formation:
                    formation = formation_data[1]
                    new_fmaccum = old_fmaccum + 3
                else:
                    formation = formation_data[0]
                    new_fmaccum = old_fmaccum + 2
                preemptable = "Yes" if constants.FORMATION_PREEMPTABLE_MAP[formation] == 1 else "No"
            else:
                formation = formation_data[0]
                new_fmaccum = old_fmaccum + 1
                preemptable = ""
            enemy_names = [constants.ENEMY_DATA[str(en)]["name"] for en in
                           constants.ENCOUNTER_DATA[str(formation)]["enemies"]]
            data_row = self.data[i]
            data_row[0].set(str(old_fmaccum) + " -> " + str(new_fmaccum))
            data_row[1].set(formation)
            data_row[2].set("\n".join(enemy_names))
            data_row[3].set(formation_type)
            data_row[4].set(preemptable)

            old_fmaccum = new_fmaccum
            last_formation = formation

    def __init__(self, app: "Application", master=None):
        super().__init__(master)
        self.app = app

        self.grid()

        tk.Label(self, width=15, text="Formation\nAccumulator").grid(row=0, column=0)
        tk.Label(self, width=15, text="Formation ID").grid(row=0, column=1)
        tk.Label(self, width=15, text="Enemies").grid(row=0, column=2)
        tk.Label(self, width=15, text="Enemy\nFormation").grid(row=0, column=3)
        tk.Label(self, width=15, text="Preemptable").grid(row=0, column=4)

        self.data = []
        for _ in range(10):
            var_list = [tk.StringVar() for _ in range(5)]
            row = len(self.data) + 1
            for i in range(len(var_list)):
                tk.Label(self, textvariable=var_list[i], width=15).grid(row=row, column=i)
            self.data.append(var_list)


class FormationExtrapolator(tk.Toplevel):

    def update_display(self):
        self.display.update_display_table()

    def __init__(self, app: "Application"):
        tk.Toplevel.__init__(self, app)
        self.app = app
        self.geometry('600x600')

        self.display: ExtrapolationTable = ExtrapolationTable(app, master=self)
