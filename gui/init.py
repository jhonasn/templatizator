import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gui.Window import Window

class GtkElements:
    def __init__(self, elements):
        for el in elements:
            if not isinstance(el, Gtk.CellRendererText):
                self.__dict__[Gtk.Buildable.get_name(el)] = el

    def new_button(label):
        return Gtk.Button.new_with_label(label)

builder = Gtk.Builder()

builder.add_from_file('./gui/gui.glade')
elements = GtkElements(builder.get_objects())

# elements.variables_treeview.get_selection().set_mode(Gtk.SELECTION_SINGLE)

window = Window(elements)
window.show(Gtk)

Gtk.main()
