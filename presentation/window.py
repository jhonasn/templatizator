from tkinter import filedialog, messagebox, Button
from domain.infrastructure import ProjectNotSetWarning
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

        Window.center(self.window)

        if application.configuration_path:
            self.label['configuration']['text'] = application.configuration_path

        self.filetree = self.application.get()
        if self.filetree and self.filetree.path:
            self.label['project']['text'] = self.filetree.path
            self.render_treeview()

    #some unicode 4len chars: ✕ ✖ ❌ ➕ ➖ ⨂ ⨁
    #5len chars: 📂
    def get_filetree_icon(self, node):
        if isinstance(node, Directory):
            return '⌹'
        elif isinstance(node, Template):
            return '⛁'
        elif isinstance(node, ConfigurableFile):
            return ''

    def get_filetree_action_icon(self, node):
        if isinstance(node, Directory):
            return '➕'
        elif isinstance(node, Template):
            return '❌'
        elif isinstance(node, ConfigurableFile):
            return ''

    def render_treeview(self):
        self.treeview.delete(*self.treeview.get_children())
        if self.filetree:
            self.fill_treeview(self.filetree)

    def fill_treeview(self, node, parent_id = ''):
        if not parent_id:
            icon = self.get_filetree_icon(node)
            action_icon = self.get_filetree_action_icon(node)
            parent_id = self.treeview.insert(
                parent_id, 'end', node.path, text=f'{icon} {node.name}',
                values=self.get_filetree_action_icon(node), open=True)

        for child in node.children:
            icon = self.get_filetree_icon(child)
            action_icon = self.get_filetree_action_icon(child)
            child_parent_id = self.treeview.insert(
                parent_id, 'end', child.path, text=f'{icon} {child.name}',
                values=action_icon,
                open=child.open if hasattr(child, 'open') else False)

            if len(child.children):
                self.fill_treeview(child, child_parent_id)

    def select_project(self):
        path = self.filetree.path
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
        self.filetree = self.application.get()
        self.render_treeview()
        self.variables.reload()

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
        ppath = self.filetree.path
        self.label['project']['text'] = ppath if ppath else 'Selecione um diretório...'
        self.variables.reload()
        self.filetree = self.application.get()
        self.render_treeview()

    def row_selected(self, event):
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
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
                    node.remove()
                    self.filetree = self.application.get()

            self.render_treeview()
        # edit
        elif type(node) is Template:
            self.editor.show(node, False, lambda: self.render_treeview())

    def row_opened(self, event):
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
        node.open = True

    def row_closed(self, event):
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
        node.open = False

    def save_templates(self):
        try:
            self.application.save_into_project()
            open_project = messagebox.askyesno(
                'Templates salvos com sucesso no projeto!',
                'Deseja abrir a pasta do projeto?',
                icon='info'
            )
            if open_project:
                OS.open_with(self.filetree.path)
        except ProjectNotSetWarning:
            messagebox.showwarning(
                'Atenção',
                'Selecione um projeto primeiramente'
            )
        except Exception:
            messagebox.showerror(
                'Erro:',
                'Não foi possível salvar os templates no projeto'
            )

    @classmethod
    def center(cls, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x_orientation = (win.winfo_screenwidth() // 2) - (width // 2)
        y_orientation = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x_orientation, y_orientation))

