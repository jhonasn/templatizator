from tkinter import Tk
import pygubu
from pygubu.builder import ttkstdwidgets

from gui.Window import Window

class App(pygubu.TkApplication):
    def start(self):
        builder = pygubu.Builder()
        # use build.add_from_string to build package
        builder.add_from_file('./gui/gui.ui')

        window = builder.get_object('window', self.master)
        Window(builder)

        self.set_title('Templatizator')

        window.mainloop()

if __name__ == '__main__':
    root = Tk()
    root.resizable(False, False)
    app = App(root)
    app.start()

