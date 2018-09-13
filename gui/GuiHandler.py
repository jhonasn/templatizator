import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import os

from src.Configuration import Configuration
from src.Node import Node

from gui.VariablesDialog import VariablesDialog
from gui.EditorDialog import EditorDialog

class GuiHandler:
    def __init__(self, app):
        builder = Gtk.Builder()

        builder.add_from_file('./gui/gui.glade')
        self.elements = GtkElements(builder.get_objects())

        self.configuration = Configuration()

        variables_dialog = VariablesDialog(self.elements)
        editor_dialog = EditorDialog(self.elements)

        self.elements.variables_button.connect('clicked', variables_dialog.show)
        self.elements.destination_filechooserbutton.connect('selection-changed', self.destination_selected)
        self.elements.configuration_filechooserbutton.connect('selection-changed', self.configuration_selected)

        self.elements.configuration_filechooserbutton.set_uri(self.configuration.configuration_path)
        self.elements.destination_filechooserbutton.set_uri(self.configuration.destination_path)

    def destination_selected(self, file_chooser):
        path = file_chooser.get_filename()
        path = path if path else self.configuration.destination_path

        parent_node = Node.from_path(path)
        #parent_node.print_node()

    def configuration_selected(self, file_chooser):
        return None

    def start(self):
        self.elements.window.show_all()
        self.elements.window.connect('destroy', Gtk.main_quit)
        Gtk.main()

class GtkElements:
    def __init__(self, elements):
        for el in elements:
            self.__dict__[Gtk.Buildable.get_name(el)] = el
