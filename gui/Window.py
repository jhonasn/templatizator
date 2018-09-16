from app import app

from src.Node import Node

from gui.VariablesSection import VariablesSection
from gui.EditorDialog import EditorDialog

class Window:
    def __init__(self, elements):
        self.elements = elements

        VariablesSection(self.elements)
        self.editor_dialog = EditorDialog(self.elements)

        self.store = self.elements.project_treestore
        self.treeview = self.elements.project_treeview

        self.elements.project_filechooserbutton.connect('selection-changed', self.project_selected)
        self.elements.configuration_filechooserbutton.connect('selection-changed', self.configuration_selected)
        self.treeview.connect('row-activated', self.row_selected)
        self.elements.templates_save_button.connect('clicked', self.save_templates)

        self.treeview.set_activate_on_single_click(True)

        if app.configuration.configuration_path:
            self.initializing = True
            self.elements.configuration_filechooserbutton.set_uri(app.configuration.configuration_path)
            self.elements.project_filechooserbutton.set_uri(app.configuration.project_path)
        self.initializing = False

    def render_treeview(self):
        self.store.clear()
        #app.configuration.nodes.print_node()
        app.configuration.nodes.fill_treestore(self.store)
        self.treeview.expand_all()

    def project_selected(self, file_chooser):
        if not self.initializing:
            path = file_chooser.get_filename()

            app.configuration.nodes = Node.from_path(path)
            app.configuration.change_project(path)

        self.render_treeview()


    def configuration_selected(self, file_chooser):
        if not self.initializing:
            app.configuration.change_configuration(file_chooser.get_filename())

    def row_selected(self, treeview, row, col):
        node = app.configuration.nodes.find_node(self.store[row][2])

        # add | remove
        if col == self.elements.project_actions_treeviewcolumn:
            # add
            if node.is_directory:
                if app.configuration.configuration_path:
                    child = node.create_child('novotemplate.[ext]')
                    self.editor_dialog.show(child, True, lambda: self.render_treeview())
                else:
                    self.elements.alert('Selecione onde salvar os templates primeiramente')
            # remove
            else:
                if self.elements.alert(
                    'Deseja realmente remover o template?',
                    message_type = 'question'
                ):
                    app.configuration.remove_template(node)

            self.render_treeview()
        # edit
        elif not node.is_directory:
            self.editor_dialog.show(node, False, lambda: self.render_treeview())

    def save_templates(self, button):
        try:
            app.configuration.save_templates_into_project()
            self.elements.alert(
                'Templates salvos com sucesso no projeto',
                message_type = 'info'
            )
        except Exception:
            self.elements.alert(
                'Não foi possível salvar os templates no projeto',
                message_type = 'error'
            )

    def show(self, gtk):
        self.elements.window.show_all()
        self.elements.window.connect('destroy', gtk.main_quit)

