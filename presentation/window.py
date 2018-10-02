from tkinter import filedialog, messagebox, Button
from domain.model import Directory, Template, ConfigurableFile

class Window:
    def __init__(self, builder, variables, editor, application):
        self.application = application

        self.variables = variables
        self.editor = editor

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

        if application.configuration_path:
            self.label['configuration']['text'] = application.configuration_path

        if application.project.path:
            self.label['project']['text'] = application.project.path
            self.render_treeview()

    #some unicode 4len chars: ✕ ✖ ❌ ➕ ➖ ⨂ ⨁
    #5len chars: 📂
    def get_filetree_icon(self, node):
        if node is Directory:
            return '⌹'
        elif node is Template:
            return '⛁'
        elif node is ConfigurableFile:
            return ''

    def get_filetree_action_icon(self, node):
        if node is Directory:
            return '➕'
        elif node is Template:
            return '❌'
        elif node is ConfigurableFile:
            return ''

    def render_treeview(self):
        self.treeview.delete(*self.treeview.get_children())
        if self.application.filetree:
            self.fill_treeview(self.application.filetree)

    def fill_treeview(self, node, parent_id = ''):
        if not parent_id:
            parent_id = treeview.insert(
                parent_id, 'end', node.path, text=f'{self.get_filetree_icon(node)} {node.name}',
                values=self.get_filetree_action_icon(node), open=True)

        for c in self.children:
            child_parent_id = treeview.insert(
                parent_id, 'end', c.path, text=f'{self.get_filetree_icon(c)} {c.name}',
                values=self.get_filetree_action_icon(node), open=c.open)
            if len(c.children):
                c.fill_treeview(treeview, child_parent_id)

    def select_project(self):
        path = self.application.project.path
        path = filedialog.askdirectory(
            title='Diretório do projeto',
            initialdir=path if path else self.application.home_path,
            mustexist=True,
            parent=self.window
        )
        if path:
            self.label['project']['text'] = path
            self.project_selected(path)

    def project_selected(self, path):
        self.application.change_path(path)
        self.render_treeview()

    def select_configuration(self):
        path = self.application.configuration_path
        path = filedialog.askdirectory(
            title='Diretório dos templates',
            initialdir=path if path else self.application.home_path,
            mustexist=True,
            parent=self.window
        )
        if path:
            self.label['configuration']['text'] = path
            self.configuration_selected(path)

    def configuration_selected(self, path):
        self.application.change_configuration_path(path)
        ppath = self.application.project.path
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

