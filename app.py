import sys
from tkinter import Tk, ttk
import pygubu
from pygubu.builder import ttkstdwidgets

from src.Util import Util

from gui.Window import Window

class App(pygubu.TkApplication):
    def start(self):
        builder = pygubu.Builder()
        # use build.add_from_string to build package
        builder.add_from_file('./gui/gui.ui')

        window = builder.get_object('window', self.master)
        Window(builder)

        self.set_title('[Templatizator]')

        window.mainloop()

if __name__ == '__main__':
    root = Tk()
    if sys.platform.find('linux') > -1:
        from ttkthemes import ThemedStyle
        root.style = ThemedStyle(root)
        if Util.is_dark_theme():
            root.style.set_theme('equilux')
        else:
            root.style.theme_use('plastik')

    root.resizable(False, False)
    app = App(root)
    app.start()

