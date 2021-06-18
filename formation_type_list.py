from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHeaderView, QAbstractItemView, QTableWidget, QTableWidgetItem, \
    QLabel

import constants

if TYPE_CHECKING:
    from main_window import MainWindow


class FormationTypeList(QDialog):

    def update_display(self):
        field_id = self.app.current_step_state.field_id
        if field_id == self.last_field:
            return  # don't update if field didn't change
        field = self.app.current_step_state.field()
        table_index = self.app.current_step_state.table_index
        table = field.table1 if field.table2 is None or table_index == 1 else field.table2
        encounters = []
        for enc_slot in table.standard:
            formation = enc_slot.formation
            if formation == 0:
                break
            rate = enc_slot.rate
            enemy_names = [constants.ENEMY_DATA[str(en)]["name"] for en in
                           constants.ENCOUNTER_DATA[str(formation)]["enemies"]]
            preemptable = "Yes" if constants.FORMATION_PREEMPTABLE_MAP[formation] == 1 else "No"
            encounters.append((" " + str(formation), " " + "\n ".join(enemy_names), " " + str(rate),
                               " " + constants.BATTLE_TYPE_NAMES[constants.FORMATION_BATTLE_TYPE_MAP[formation]],
                               " " + preemptable))
        for enc_slot in table.special:
            formation = enc_slot.formation
            if formation == 0:
                break
            rate = enc_slot.rate
            enemy_names = [constants.ENEMY_DATA[str(en)]["name"] for en in
                           constants.ENCOUNTER_DATA[str(formation)]["enemies"]]
            preemptable = "---"
            encounters.append((" " + str(formation), " " + "\n ".join(enemy_names), " " + str(rate),
                               " " + constants.BATTLE_TYPE_NAMES[constants.FORMATION_BATTLE_TYPE_MAP[formation]],
                               " " + preemptable))
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if i < len(encounters):
                    self.table.cellWidget(i, j).setText(encounters[i][j])
                else:
                    self.table.cellWidget(i, j).setText("")
        self.table.resizeRowsToContents()
        self.last_field = field_id

    def __init__(self, app: "MainWindow", parent=None):
        super(FormationTypeList, self).__init__(app)
        self.app = app

        self.last_field = None

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
        labels = ["Formation ID", "Enemies", "Encounter\nRate", "Enemy\nFormation", "Preemptable"]
        for i in range(len(labels)):
            self.table.setHorizontalHeaderItem(i, QTableWidgetItem(labels[i]))
            for j in range(self.table.rowCount()):
                self.table.setCellWidget(j, i, QLabel())
        for i in range(self.table.rowCount()):
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(""))
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.show()
