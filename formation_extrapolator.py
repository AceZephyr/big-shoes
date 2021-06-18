from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QAbstractItemView, QTableWidgetItem, QLabel, \
    QHeaderView

import constants
import formations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class FormationExtrapolator(QDialog):

    def update_display(self):
        field = self.app.current_step_state.field()
        preempt_rate = self.app.current_step_state.preempt_rate
        table = self.app.current_step_state.table_index
        old_fmaccum = self.app.current_step_state.formation_value
        last_formation = self.app.current_step_state.last_encounter_formation
        for i in range(10):
            formation_data = field.encounter_on_formation(formation=old_fmaccum,
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
                preemptable = "---"
            enemy_names = [constants.ENEMY_DATA[str(en)]["name"] for en in
                           constants.ENCOUNTER_DATA[str(formation)]["enemies"]]
            self.table.cellWidget(i, 0).setText(" " + str(old_fmaccum) + " -> " + str(new_fmaccum))
            self.table.cellWidget(i, 1).setText(" " + str(formation))
            self.table.cellWidget(i, 2).setText(" " + "\n ".join(enemy_names))
            self.table.cellWidget(i, 3).setText(" " + formation_type)
            self.table.cellWidget(i, 4).setText(" " + preemptable)

            old_fmaccum = new_fmaccum
            last_formation = formation
        self.table.resizeRowsToContents()

    def __init__(self, app: "MainWindow", parent=None):
        super(FormationExtrapolator, self).__init__(app)
        self.app = app

        self.setWindowTitle(self.app.windowTitle())
        self.setWindowIcon(self.app.windowIcon())

        layout = QVBoxLayout()

        self.table = QTableWidget(10, 5)
        self.table.setMinimumWidth(500)
        self.table.setMinimumHeight(500)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        labels = ["Formation\nAccumulator", "Formation ID", "Enemies", "Enemy\nFormation", "Preemptable"]
        for i in range(len(labels)):
            self.table.setHorizontalHeaderItem(i, QTableWidgetItem(labels[i]))
            for j in range(self.table.rowCount()):
                self.table.setCellWidget(j, i, QLabel())
        for i in range(self.table.rowCount()):
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(""))
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.show()
