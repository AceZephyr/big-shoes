import constants
import formations

import tkinter as tk
from tkinter import ttk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import Application


class ListTable(tk.LabelFrame):

    def update_display_table(self):
        pass

    def __init__(self, app: "Application", master=None):
        super().__init__(master, borderwidth=1, text="Formations", relief=tk.SOLID)
        self.app = app


class FormationList(tk.Toplevel):
    def update_display(self):
        self.display.update_display_table()

    def __init__(self, app: "Application"):
        tk.Toplevel.__init__(self, app)
        self.app = app
        self.geometry('600x600')

        self.display: ListTable = ListTable(app, master=self)
