from os.path import expanduser as get_path
from tkinter import filedialog, messagebox, Button

from presentation.application import builder

#from src.Configuration import configuration
#from src.Util import Util

#from gui.VariablesSection import VariablesSection
#from gui.EditorDialog import EditorDialog

class Window:
    def __init__(self):
        #self.variables_section = VariablesSection(builder)
        #self.editor_dialog = EditorDialog(builder)

        self.window = builder.get_object('window_toplevel')
        self.treeview = builder.get_object('project_treeview')

        self.label = {
            'project': builder.get_object('project_file_label'),
            'configuration': builder.get_object('configuration_file_label')
        }

        builder.get_object('project_file_button')['command'] = self.select_project
        builder.get_object('configuration_file_button')['command'] = self.select_configuration
        builder.get_object('templates_save_button')['command'] = self.save_templates
        self.treeview.bind('<ButtonRelease-1>', self.row_selected)
        self.treeview.bind('<<TreeviewOpen>>', self.row_opened)
        self.treeview.bind('<<TreeviewClose>>', self.row_closed)

        '''
        if configuration.configuration_path:
            self.label['configuration']['text'] = configuration.configuration_path
            self.label['project']['text'] = configuration.project_path
            self.render_treeview()
        '''

'''
    #some unicode 4len chars: ✕ ✖ ❌ ➕ ➖ ⨂ ⨁
    #5len chars: 📂
    def get_name(self):
        return f'⌹ {self.name}' if self.is_directory else f'⛁ {self.name}'

    def get_actions(self):
        return '➕' if self.is_directory else'❌'
'''

    def render_treeview(self):
        self.treeview.delete(*self.treeview.get_children())
        if configuration.nodes:
            configuration.nodes.fill_treeview(self.treeview)

    def select_project(self):
        path = configuration.project_path
        path = filedialog.askdirectory(
            title='Diretório do projeto',
            initialdir=path if path else get_path('~'),
            mustexist=True,
            parent=self.window
        )
        if path:
            self.label['project']['text'] = path
            self.project_selected(path)

    def project_selected(self, path):
        configuration.change_project(path)
        self.render_treeview()

    def select_configuration(self):
        path = configuration.configuration_path
        path = filedialog.askdirectory(
            title='Diretório dos templates',
            initialdir=path if path else get_path('~'),
            mustexist=True,
            parent=self.window
        )
        if path:
            self.label['configuration']['text'] = path
            self.configuration_selected(path)

    def configuration_selected(self, path):
        configuration.change_configuration(path)
        ppath = configuration.project_path
        self.label['project']['text'] = ppath if ppath else 'Selecione um diretório...'
        self.variables_section.reload()
        self.render_treeview()

    def row_selected(self, event):
        selected_path = self.treeview.focus()
        node = configuration.nodes.find_node(selected_path)
        col = self.treeview.identify_column(event.x)

        # add | remove
        if col == '#1':
            # add
            if node.is_directory:
                if configuration.configuration_path:
                    node.open = True
                    child = node.create_child('novotemplate.[ext]')
                    self.editor_dialog.show(child, True, lambda: self.render_treeview())
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
            self.editor_dialog.show(node, False, lambda: self.render_treeview())

    def row_opened(self, event):
        selected_path = self.treeview.focus()
        node = configuration.nodes.find_node(selected_path)
        node.open = True

    def row_closed(self, event):
        selected_path = self.treeview.focus()
        node = configuration.nodes.find_node(selected_path)
        node.open = False

    def save_templates(self):
        try:
            configuration.save_templates_into_project()
            openProject = messagebox.askyesno(
                'Templates salvos com sucesso no projeto!',
                'Deseja abrir a pasta do projeto?',
                icon='info'
            )
            if openProject:
                Util.open_path_with_os(configuration.project_path)
        except Exception:
            messagebox.showerror(
                'Erro:',
                'Não foi possível salvar os templates no projeto'
            )

