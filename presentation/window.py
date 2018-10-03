from tkinter import filedialog, messagebox, Button
from domain.model import Directory, Template, ConfigurableFile
from domain.helper import OS

class Window:
    def __init__(self, builder, variables, editor, application, template_application, configurable_application):
        self.application = application
        self.template_application = template_application
        self.configurable_application = configurable_application

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

        self.center(self.window)

        if application.configuration_path:
            self.label['configuration']['text'] = application.configuration_path

        if application.filetree.path:
            self.label['project']['text'] = application.filetree.path
            self.render_treeview()

    #some unicode 4len chars: ✕ ✖ ❌ ➕ ➖ ⨂ ⨁
    #5len chars: 📂
    def get_filetree_icon(self, node):
        if isinstance(node, Directory):
            return '⌹'
        elif type(node) is Template:
            return '⛁'
        elif type(node) is ConfigurableFile:
            return ''

    def get_filetree_action_icon(self, node):
        if isinstance(node, Directory):
            return '➕'
        elif type(node) is Template:
            return '❌'
        elif type(node) is ConfigurableFile:
            return ''

    def render_treeview(self):
        self.treeview.delete(*self.treeview.get_children())
        if self.application.filetree:
            self.fill_treeview(self.application.filetree)

    def fill_treeview(self, node, parent_id = ''):
        if not parent_id:
            parent_id = self.treeview.insert(
                parent_id, 'end', node.path, text=f'{self.get_filetree_icon(node)} {node.name}',
                values=self.get_filetree_action_icon(node), open=True)

        for c in node.children:
            child_parent_id = self.treeview.insert(
                parent_id, 'end', c.path, text=f'{self.get_filetree_icon(c)} {c.name}',
                values=self.get_filetree_action_icon(node), open=c.open if hasattr(c, 'open') else False)
            if len(c.children):
                self.fill_treeview(c, child_parent_id)

    def select_project(self):
        path = self.application.filetree.path
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
        ppath = self.application.filetree.path
        self.label['project']['text'] = ppath if ppath else 'Selecione um diretório...'
        self.variables.reload()
        self.render_treeview()

    def row_selected(self, event):
        selected_path = self.treeview.focus()
        node = self.application.find_node(selected_path)
        col = self.treeview.identify_column(event.x)

        # add | remove
        if col == '#1':
            # add
            if isinstance(node, Directory):
                if self.application.configuration_path:
                    node.open = True
                    child = self.template_application.create_child(node, 'novotemplate.[ext]')
                    self.editor.show(child, True, lambda: self.render_treeview())
                else:
                    messagebox.showwarning('Atenção:', 'Selecione onde salvar os templates primeiramente')
            # remove
            else:
                if messagebox.askyesno(
                    'Pergunta:',
                    'Deseja realmente remover o template?'
                ):
                    self.template_application.remove(node)

            self.render_treeview()
        # edit
        elif type(node) is not Directory:
            self.editor.show(node, False, lambda: self.render_treeview())

    def row_opened(self, event):
        selected_path = self.treeview.focus()
        node = self.application.find_node(selected_path)
        node.open = True

    def row_closed(self, event):
        selected_path = self.treeview.focus()
        node = self.application.find_node(selected_path)
        node.open = False

    def save_templates(self):
        try:
            self.application.save_into_project()
            openProject = messagebox.askyesno(
                'Templates salvos com sucesso no projeto!',
                'Deseja abrir a pasta do projeto?',
                icon='info'
            )
            if openProject:
                OS.open_with(self.application.filetree.path)
        except Exception:
            messagebox.showerror(
                'Erro:',
                'Não foi possível salvar os templates no projeto'
            )

    def center(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

