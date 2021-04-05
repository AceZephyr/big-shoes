import tkinter as tk
import threading
import stepgraph


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        menubar = tk.Menu(self)

        menu_file = tk.Menu(menubar, tearoff=0)
        menu_file.add_command(label="Exit", command=self.quit)

        menu_connect = tk.Menu(menubar, tearoff=0)
        menu_connect.add_command(label="Connect to Emulator", command=lambda: 0)
        menu_connect.add_command(label="Connect to PC", command=lambda: 0)
        menu_connect.add_separator()
        menu_connect.add_command(label="Disconnect", command=lambda: 0)

        menubar.add_cascade(label="File", menu=menu_file)
        menubar.add_cascade(label="Connect", menu=menu_connect)

        self.master.config(menu=menubar)


if __name__ == '__main__':
    app = Application()
    app.master.title("Big Shoes")
    app.master.iconphoto(False, tk.PhotoImage(file="icon.png"))

    stepthread = threading.Thread(target=stepgraph.main)
    stepthread.start()

    app.mainloop()

    stepgraph.running = False
