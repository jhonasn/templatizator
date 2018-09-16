import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gui.Window import Window

class GtkElements:
    def __init__(self, elements):
        for el in elements:
            if isinstance(el, Gtk.Buildable):
                self.__dict__[Gtk.Buildable.get_name(el)] = el

    def alert(self, message, title = None, message_type = 'warning'):
        msg_type = {
            'info': Gtk.MessageType.INFO,
            'warning': Gtk.MessageType.WARNING,
            'error': Gtk.MessageType.ERROR,
            'question': Gtk.MessageType.QUESTION
        }.get(message_type, None)

        if not title:
            title = {
                'info': 'Informação:',
                'warning': 'Atenção:',
                'error': 'Erro:',
                'question': 'Pergunta:'
            }.get(message_type)

        dialog = Gtk.MessageDialog(self.window,
            0, msg_type,
            Gtk.ButtonsType.OK if message_type != 'question' else Gtk.ButtonsType.YES_NO,
            title)
        dialog.format_secondary_text(message)
        response = dialog.run()
        
        dialog.destroy()
        return response == Gtk.ResponseType.YES

builder = Gtk.Builder()

builder.add_from_file('./gui/gui_new.glade')
elements = GtkElements(builder.get_objects())

window = Window(elements)
window.show(Gtk)

Gtk.main()

