from src.Configuration import Configuration
from src.Node import Node

from gui.VariablesDialog import VariablesDialog
from gui.EditorDialog import EditorDialog

class Window:
    def __init__(self, elements):
        self.elements = elements

        self.configuration = Configuration()

        variables_dialog = VariablesDialog(self.elements)
        self.editor_dialog = EditorDialog(self.elements)

        self.store = self.elements.destination_treestore
        self.treeview = self.elements.destination_treeview

        self.elements.variables_button.connect('clicked', variables_dialog.show)
        self.elements.destination_filechooserbutton.connect('selection-changed', self.destination_selected)
        self.elements.configuration_filechooserbutton.connect('selection-changed', self.configuration_selected)
        self.treeview.connect('row-activated', self.add_remove_template)

        self.treeview.set_activate_on_single_click(True)

        self.elements.configuration_filechooserbutton.set_uri(self.configuration.configuration_path)
        self.elements.destination_filechooserbutton.set_uri(self.configuration.destination_path)

    def render_treeview(self):
        self.store.clear()
        #self.nodes.print_node()
        self.nodes.fill_treestore(self.store)
        self.treeview.expand_all()

    def destination_selected(self, file_chooser):
        path = file_chooser.get_filename()
        path = path if path else self.configuration.destination_path

        self.nodes = Node.from_path(path)
        self.render_treeview()

    def configuration_selected(self, file_chooser):
        return None

    def add_remove_template(self, treeview, row, col):
        if col == self.elements.destination_actions_treeviewcolumn:
            node = self.nodes.find_node(self.store[row][2])
            if node.is_directory:
                child = node.create_child('[nome]_template.py')
                child.is_new = True
                self.editor_dialog.show(child, lambda: self.render_treeview())
            else:
                node.remove()

            self.render_treeview()

    def show(self, gtk):
        self.elements.window.show_all()
        self.elements.window.connect('destroy', gtk.main_quit)
