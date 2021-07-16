import sys

import win32gui
import win32process
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QMenuBar, QMenu, QFrame, QApplication, QTableWidget, QLabel, \
    QAbstractItemView, QTableWidgetItem, QMessageBox, QDialog, QComboBox, QGridLayout, QPushButton, QHeaderView

import formation_extrapolator
import formation_type_list

import hook
import settings
import stepgraph
from constants import *


class ConnectEmuDialog(QDialog):

    def on_emu_select(self, index):
        self.process_select.clear()
        self.process_select.insertItems(0, sorted(list([str(x) for x in self.pids[self.emu_select.itemText(index)]])))
        self.version_select.clear()
        self.version_select.insertItems(0, [x.name for x in hook.Hook.EMULATOR_MAP[self.emu_select.itemText(index)][1]])

    def show_window_button(self):
        def _callback(hwnd, pid):
            thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
            if process_id == pid:
                win32gui.BringWindowToTop(hwnd)

        win32gui.EnumWindows(_callback, int(self.process_select.currentText()))

    def connect_button(self):
        for platform_version in hook.Hook.EMULATOR_MAP[self.emu_select.currentText()]:
            if platform_version[1].name == self.version_select.currentText():
                self.parent_app.hook.hooked_platform = platform_version
                self.parent_app.hook.hooked_process_id = int(self.process_select.currentText())
                self.parent_app.hook.start()
                self.close()

    def __init__(self, pids, parent_app: "MainWindow", parent=None):
        super(ConnectEmuDialog, self).__init__(parent)

        self.pids = pids

        self.parent_app = parent_app

        layout = QGridLayout()

        self.emu_select = QComboBox(self)
        self.emu_select.insertItems(0, sorted(list(self.pids.keys()), key=lambda x: x.lower()))

        self.process_select = QComboBox(self)

        self.version_select = QComboBox(self)

        self.emu_select.activated.connect(self.on_emu_select)

        self.on_emu_select(0)

        layout.addWidget(QLabel("Emulator Name:"), 0, 0)
        layout.addWidget(QLabel("Emulator Process ID:"), 0, 1)
        layout.addWidget(QLabel("Emulator Version:"), 0, 2)
        layout.addWidget(self.emu_select, 1, 0)
        layout.addWidget(self.process_select, 1, 1)
        layout.addWidget(self.version_select, 1, 2)

        button_show_this_window = QPushButton("Show This Window")
        button_show_this_window.clicked.connect(self.show_window_button)
        layout.addWidget(button_show_this_window, 2, 1)

        button_connect = QPushButton("Connect")
        button_connect.clicked.connect(self.connect_button)
        button_connect.setDefault(True)
        layout.addWidget(button_connect, 3, 1)

        self.setLayout(layout)


class MainWindow(QMainWindow):

    def open_formation_extrapolator(self):
        self.formation_extrapolator_windows.append(formation_extrapolator.FormationExtrapolator(self))

    def open_list_formation_types(self):
        self.list_formation_types_windows.append(formation_type_list.FormationTypeList(self))

    def update_formation_windows(self):
        for window in self.formation_extrapolator_windows:
            window.update_display()
        for window in self.list_formation_types_windows:
            window.update_display()

    def disconnect(self):
        self.hook.stop()

    def connect_pc(self):
        if self.hook.running:
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("Already Connected")
            box.setText("Already connected. Disconnect first.")
            box.setStandardButtons(QMessageBox.Ok)
            box.exec()
            return
        pid = hook.get_pc_process_id()
        if pid is None:
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("FF7 PC Not Detected")
            box.setText("FF7 PC was not detected.")
            box.setStandardButtons(QMessageBox.Ok)
            box.exec()
            return
        self.hook.hooked_platform = hook.Hook.PC_PLATFORM
        self.hook.hooked_process_id = pid
        self.hook.start()

    def connect_emulator(self):
        if self.hook.running:
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("Already Connected")
            box.setText("Already connected. Disconnect first.")
            box.setStandardButtons(QMessageBox.Ok)
            box.exec()
            return
        pids = hook.get_emu_process_ids()
        if len(pids) == 0:
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("No Emulators Detected")
            box.setText("No emulators that can be connected to were detected.")
            box.setStandardButtons(QMessageBox.Ok)
            box.exec()
            return
        ConnectEmuDialog(pids, self).exec()

    def closeEvent(self, event):
        self.stepgraph.stop()
        self.disconnect()

    def _exit(self):
        self.stepgraph.stop()
        self.disconnect()
        exit()

    def __init__(self, _settings: settings.Settings, parent=None):
        super(MainWindow, self).__init__(parent)

        self.formation_extrapolator_windows = []
        self.list_formation_types_windows = []

        self.settings = _settings

        self.stepgraph = stepgraph.Stepgraph(self)

        self.hook = hook.Hook(self)

        self.current_step_state: State = State(field_id=117, step=Step(0, 0), danger=0, step_fraction=0,
                                               formation_value=0)

        self.setWindowTitle(self.settings.WINDOW_TITLE)
        self.setWindowIcon(QIcon(self.settings.WINDOW_ICON))

        menubar = QMenuBar()

        menu_file = QMenu("File")

        menu_file_exit = QAction("Exit", self)
        menu_file_exit.triggered.connect(self._exit)
        menu_file.addAction(menu_file_exit)

        menu_connect = QMenu("Connect")

        menu_connect_connect_emulator = QAction("Connect to Emulator", self)
        menu_connect_connect_emulator.triggered.connect(self.connect_emulator)
        menu_connect.addAction(menu_connect_connect_emulator)

        menu_connect_connect_pc = QAction("Connect to PC", self)
        menu_connect_connect_pc.triggered.connect(self.connect_pc)
        menu_connect.addAction(menu_connect_connect_pc)

        menu_connect.addSeparator()

        menu_connect_disconnect = QAction("Disconnect", self)
        menu_connect_disconnect.triggered.connect(self.disconnect)
        menu_connect.addAction(menu_connect_disconnect)

        menu_window = QMenu("Window")

        menu_window_toggle_stepgraph = QAction("Toggle Stepgraph", self)
        menu_window_toggle_stepgraph.triggered.connect(self.stepgraph.toggle)
        menu_window.addAction(menu_window_toggle_stepgraph)

        menu_window.addSeparator()

        menu_window_formation_extrapolator = QAction("Formation Extrapolator", self)
        menu_window_formation_extrapolator.triggered.connect(self.open_formation_extrapolator)
        menu_window.addAction(menu_window_formation_extrapolator)

        menu_window_list_formation_types = QAction("List Formation Types", self)
        menu_window_list_formation_types.triggered.connect(self.open_list_formation_types)
        menu_window.addAction(menu_window_list_formation_types)

        menubar.addMenu(menu_file)
        menubar.addMenu(menu_connect)
        menubar.addMenu(menu_window)

        self.setMenuBar(menubar)

        main_frame = QFrame()
        layout = QVBoxLayout()

        rows = ["Step ID", "Step Fraction", "Offset", "Danger", "Formation Accumulator", "Field ID", "Table Index",
                "Danger Divisor Multiplier", "Lure Rate", "Preempt Rate", "Last Encounter Formation"]

        self.memory_view = QTableWidget(len(rows), 2)
        self.memory_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.memory_view.setFocusPolicy(Qt.NoFocus)
        self.memory_view.setSelectionMode(QAbstractItemView.NoSelection)
        self.memory_view.setHorizontalHeaderItem(0, QTableWidgetItem("Address"))
        self.memory_view.setHorizontalHeaderItem(1, QTableWidgetItem("        Value        "))
        self.memory_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.memory_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for rowNum in range(len(rows)):
            self.memory_view.setVerticalHeaderItem(rowNum, QTableWidgetItem(""))
            _l = QLabel(" " + rows[rowNum] + " ")
            _l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.memory_view.setCellWidget(rowNum, 0, _l)
            _l = QLabel("")
            _l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.memory_view.setCellWidget(rowNum, 1, _l)
        self.memory_view.resizeColumnsToContents()
        self.memory_view.setMinimumHeight(350)
        self.memory_view.setMinimumWidth(300)
        layout.addWidget(self.memory_view)

        self.connected_text = QLabel(self.settings.DISCONNECTED_TEXT)
        self.connected_text.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.connected_text)

        main_frame.setLayout(layout)

        self.setCentralWidget(main_frame)

        self.setMinimumHeight(420)


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication()
    # Create and show the form
    main_window = MainWindow(settings.Settings())
    main_window.show()
    # Run the main Qt loop
    sys.exit(app.exec())
