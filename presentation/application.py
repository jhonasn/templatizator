from tkinter import Tk, ttk
import pygubu
from pygubu.builder import ttkstdwidgets

from domain.helper import OS

builder = pygubu.Builder()

class Application:
    def __init__(self):
        # use build.add_from_string to build package
        builder.add_from_file('./presentation/interface.ui')

        root = builder.get_object('window_toplevel')
        self.root = root

        if OS.is_linux:
            from ttkthemes import ThemedStyle
            root.style = ThemedStyle(root)
            if OS.is_dark_theme():
                root.style.set_theme('equilux')
            else:
                root.style.theme_use('plastik')

    def start(self):
        from presentation.window import Window
        from presentation.variables import Variables
        from presentation.editor import Editor

        self.window = Window()
        self.variables = Variables()
        self.editor = Editor()

        self.root.mainloop()
        
app = Application()

