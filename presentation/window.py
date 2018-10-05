'''Handler for main window GUI actions that includes:
- Choosing configuration and project folder;
- Show project file tree view;
    - Handle directories and files actions;
- Call editor window;
- Call save files into the project action.
'''
from tkinter import filedialog, messagebox
from domain.infrastructure import ProjectNotSetWarning
from domain.model import Directory, Template, ConfigurableFile
from domain.helper import OS

# pylint: disable=too-many-instance-attributes
class Window:
    '''Class handles for GUI main window'''
    # pylint: disable=too-many-arguments
    def __init__(self, builder, variables, editor, application,
                 template_application, configurable_application):
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
    @classmethod
    def get_filetree_icon(cls, node):
        '''Get filetree icon according the filetree node type'''
        return {
            Directory: '⌹',
            Template: '⛁',
            ConfigurableFile: ''
        }.get(type(node))

    @classmethod
    def get_filetree_action_icon(cls, node):
        '''Get filetree icon for action (include or delete) according the filetree node type'''
        return {
            Directory: '➕',
            Template: '❌',
            ConfigurableFile: ''
        }.get(type(node))

    def render_treeview(self):
        '''Render treeview if there is filetree instance set'''
        self.treeview.delete(*self.treeview.get_children())
        if self.filetree:
            self.fill_treeview(self.filetree)

    def fill_treeview(self, node, parent_id=''):
        '''Recursive method that fills the project treeview with application filetree result'''
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

            if child.children:
                self.fill_treeview(child, child_parent_id)

    def select_project(self):
        '''Calls project path selector window to set the project path'''
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
        '''Handle project selected path calling application layer and re-rendering items'''
        self.application.change_path(path)
        self.filetree = self.application.get()
        self.render_treeview()
        self.variables.reload()

    def select_configuration(self):
        '''Calls configuration path selector window to set the configuration path'''
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
        '''Handle configuration selected path calling application layer and re-rendering items'''
        self.application.change_configuration_path(path)
        ppath = self.filetree.path
        self.label['project']['text'] = ppath if ppath else 'Selecione um diretório...'
        self.variables.reload()
        self.filetree = self.application.get()
        self.render_treeview()

    def row_selected(self, event):
        '''Call apropriated action when a treeview row is clicked, those action will be
        add, remove or edit template. When the action is add or edit the editor window
        is called. When remove action is called a confirmation dialog will be shown.
        '''
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
                    self.editor.show(child, True, self.render_treeview())
                else:
                    messagebox.showwarning(
                        'Atenção:',
                        'Selecione onde salvar os templates primeiramente'
                    )
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
        elif isinstance(node, Template):
            self.editor.show(node, False, self.render_treeview())

    # pylint: disable=unused-argument
    def row_opened(self, event):
        '''When project treeview directory is opened "save" the directory open state'''
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
        node.open = True

    # pylint: disable=unused-argument
    def row_closed(self, event):
        '''When project treeview directory is closed "save" the directory open state'''
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
        node.open = False

    def save_templates(self):
        '''Call aplication layer to save the templates into the project folder.
        After the files are recorded asks user if he wants to open the project directory.
        Show a default error dialog if something goes wrong'''
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
        except Exception as ex:
            messagebox.showerror(
                'Erro:',
                'Não foi possível salvar os templates no projeto'
            )
            raise ex

    @classmethod
    def center(cls, win):
        '''Centers the informed window into the desktop screen'''
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x_orientation = (win.winfo_screenwidth() // 2) - (width // 2)
        y_orientation = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x_orientation, y_orientation))
