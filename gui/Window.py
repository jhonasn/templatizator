from tkinter import filedialog, messagebox, Button

from src.Configuration import configuration

from src.Node import Node

from gui.VariablesSection import VariablesSection
from gui.EditorDialog import EditorDialog

class Window:
    def __init__(self, builder):
        self.variables_section = VariablesSection(builder)
        self.editor_dialog = EditorDialog(builder)

        self.treeview = builder.get_object('project_treeview')

        self.label = {
            'project': builder.get_object('project_file_label'),
            'configuration': builder.get_object('configuration_file_label')
        }

        builder.get_object('project_file_button')['command'] = self.select_project
        builder.get_object('configuration_file_button')['command'] = self.select_configuration
        builder.get_object('templates_save_button')['command'] = self.save_templates
        self.treeview.bind('<ButtonRelease-1>', self.row_selected)

        if configuration.configuration_path:
            self.label['configuration']['text'] = configuration.configuration_path
            self.label['project']['text'] = configuration.project_path
            self.render_treeview()

    def render_treeview(self):
        if configuration.nodes:
            self.treeview.delete(*self.treeview.get_children())
            configuration.nodes.fill_treeview(self.treeview)

    def select_project(self):
        path = filedialog.askdirectory()
        if path:
            self.label['project']['text'] = path
            self.project_selected(path)

    def project_selected(self, path):
        configuration.nodes = Node.from_path(path)
        configuration.change_project(path)

        self.render_treeview()

    def select_configuration(self):
        path = filedialog.askdirectory()
        if path:
            self.label['configuration']['text'] = path
            self.configuration_selected(path)

    def configuration_selected(self, path):
        configuration.change_configuration(path)

    def row_selected(self, event):
        selected_path = self.treeview.focus()
        node = configuration.nodes.find_node(selected_path)
        col = self.treeview.identify_column(event.x)

        # add | remove
        if col == '#1':
            # add
            if node.is_directory:
                if configuration.configuration_path:
                    child = node.create_child('novotemplate.[ext]')
                    #TODO: implement show/hide editor window
                    #self.editor_dialog.show(child, True, lambda: self.render_treeview())
                else:
                    messagebox.showwarning('Atenção:', 'Selecione onde salvar os templates primeiramente')
            # remove
            else:
                if messagebox.askyesno(
                    'Pergunta:',
                    'Deseja realmente remover o template?'
                ):
                    configuration.remove_template(node)

            self.render_treeview()
        # edit
        elif not node.is_directory:
            print('implement show editor dialog')
            #self.editor_dialog.show(node, False, lambda: self.render_treeview())

    def save_templates(self, button):
        try:
            configuration.save_templates_into_project()
            messagebox.showinfo(
                'Informação:',
                'Templates salvos com sucesso no projeto'
            )
        except Exception:
            messagebox.showerror(
                'Erro:',
                'Não foi possível salvar os templates no projeto'
            )

