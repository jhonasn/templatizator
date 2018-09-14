import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gui.Window import Window

class GtkElements:
    def __init__(self, elements):
        for el in elements:
            if isinstance(el, Gtk.Buildable):
                self.__dict__[Gtk.Buildable.get_name(el)] = el

    def alert(self, message, detail = ''):
        dialog = Gtk.MessageDialog(self.window,
            0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            message)
        dialog.format_secondary_text(detail)
        dialog.run()
        dialog.destroy()

builder = Gtk.Builder()

builder.add_from_file('./gui/gui.glade')
elements = GtkElements(builder.get_objects())

window = Window(elements)
window.show(Gtk)

Gtk.main()
