from tkinter import Tk, ttk
import pygubu
from pygubu.builder import ttkstdwidgets

from domain.helper import OS
from presentation.container import Container

builder = pygubu.Builder()

# use build.add_from_string to build package
builder.add_from_file('./presentation/interface.ui')

root = builder.get_object('window_toplevel')

if OS.is_linux:
    from ttkthemes import ThemedStyle
    root.style = ThemedStyle(root)
    if OS.is_dark_theme():
        root.style.set_theme('equilux')
    else:
        root.style.theme_use('plastik')

def initialize():
    Container.configure(builder)
    root.mainloop()

