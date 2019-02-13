'''Initialize the GUI'''
import pygubu
# import ttkstdwidgets is necessary for building
from pygubu.builder import ttkstdwidgets  # noqa: F401
from templatizator.domain.helper import OS
from templatizator.presentation.container import Container


def initialize():
    '''Initialize the application first initializing the container
    that expects that domain container is initialized
    and after call the GUI window loop to show the GUI
    '''
    builder = pygubu.Builder()

    # use build.add_from_string to build package
    builder.add_from_file(
        OS.get_path('templatizator/presentation/interface.ui'))

    root = builder.get_object('window_toplevel')

    if OS.is_linux:
        from ttkthemes import ThemedStyle
        root.style = ThemedStyle(root)
        if OS.is_dark_theme():
            root.style.set_theme('equilux')
        else:
            root.style.theme_use('plastik')

    Container.configure(builder)
    root.mainloop()
