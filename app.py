from tkinter import Tk
import pygubu

from gui.Window import Window

class App(pygubu.TkApplication):
    def start(self):
        builder = pygubu.Builder()
        builder.add_from_file('./gui/gui.ui')

        window = builder.get_object('window', self.master)

        Window(builder)

        builder.connect_callbacks(window)

        window.mainloop()

if __name__ == '__main__':
    app = App(Tk())
    app.start()

