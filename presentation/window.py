'''Handler for main window GUI actions that includes:
- Choosing configuration and project folder;
- Show project file tree view;
    - Handle directories and files actions;
- Call editor window;
- Call save files into the project action.
'''
from tkinter import filedialog, messagebox, Menu
from domain.infrastructure import ProjectNotSetWarning
from domain.model import Directory, File, Template, ConfigurableFile
from domain.helper import OS
from presentation.helper import get_tkinter_unicode
from presentation.widgets import Tooltip


# pylint: disable=too-many-instance-attributes
class Window:
    '''Class handles for GUI main window'''
    # pylint: disable=too-many-arguments
    def __init__(self, builder, variables, editor, application,
                 template_application, configurable_application):
        self.application = application
        self.template_application = template_application
        self.configurable_application = configurable_application

        # selected node
        self.node = None

        self.variables = variables
        self.editor = editor

        self.window = builder.get_object('window_toplevel')
        self.treeview = builder.get_object('project_treeview')
        self.directory_menu = Menu(self.treeview, tearoff=0)
        self.directory_menu.add_command(label='Add template',
                                        command=self.add_template)
        self.directory_menu.add_command(label='Add configurable',
                                        command=self.add_configurable)
        self.file_menu = Menu(self.treeview, tearoff=0)
        self.file_menu.add_command(label='Abrir', command=self.open_file)
        self.file_menu.add_command(label='Abrir com...',
                                   command=self.open_with)
        self.file_menu.add_command(label='Remover', command=self.remove_file)
        Tooltip(self.treeview, col='#', before=self.before_show_tooltip)

        self.label = {
            'project': builder.get_object('project_file_label'),
            'configuration': builder.get_object('configuration_file_label')
        }

        builder.get_object('project_file_button')['command'] = \
            self.select_project
        builder.get_object('configuration_file_button')['command'] = \
            self.select_configuration
        builder.get_object('templates_save_button')['command'] = \
            self.save_templates
        self.treeview.bind('<ButtonRelease-1>', self.row_selected)
        self.treeview.bind('<<TreeviewOpen>>', self.row_opened)
        self.treeview.bind('<<TreeviewClose>>', self.row_closed)
        self.treeview.bind('<ButtonRelease-3>', self.row_popup_selected)

        Window.center(self.window)

        if application.configuration_path:
            self.label['configuration']['text'] = \
                application.configuration_path

        self.filetree = self.application.get()
        if self.filetree and self.filetree.path:
            self.label['project']['text'] = self.filetree.path
            self.render_treeview()

    @classmethod
    def get_filetree_icon(cls, node):
        '''Get filetree icon according the filetree node type'''
        icon = ''
        if isinstance(node, Directory):
            icon = '\U0001F4C2' if node.open else '\U0001F4C1'
        if isinstance(node, Template):
            icon = '\U0001F5CB'
        if isinstance(node, ConfigurableFile):
            icon = '\U0001F5CE'
        return get_tkinter_unicode(icon)

    @classmethod
    def get_filetree_action_icon(cls, node):
        '''Get filetree icon for action (include or delete)
        according the filetree node type
        '''
        icon = '\U00002795' if isinstance(node, Directory) else '\U0000274C'
        return get_tkinter_unicode(icon)

    @classmethod
    def get_filetree_checkbox(cls, node):
        '''Get checkbox and its state
        If the node is a file then the checkbox is shown checked or not
        depending on node state.
        If the node is a directory don't show the checkbox
        '''
        icon = ''
        if isinstance(node, File):
            icon = '\U00002611' if node.save else '\U00002612'
        return get_tkinter_unicode(icon)

    def render_treeview(self):
        '''Render treeview if there is filetree instance set'''
        self.treeview.delete(*self.treeview.get_children())
        if self.filetree:
            self.fill_treeview(self.filetree)

    def fill_treeview(self, node, parent_id=''):
        '''Recursive method that fills the project treeview
        with application filetree result
        '''
        if not parent_id:
            icon = self.get_filetree_icon(node)
            action_icon = self.get_filetree_action_icon(node)
            checkbox = self.get_filetree_checkbox(node)
            name = f'{icon} {node.name}'
            parent_id = self.treeview.insert(
                parent_id, 'end', node.path, text=name,
                values=(checkbox, action_icon), open=True
            )

        for child in node.children:
            icon = self.get_filetree_icon(child)
            action_icon = self.get_filetree_action_icon(child)
            name = f'{icon} {child.name}'
            checkbox = self.get_filetree_checkbox(child)
            child_parent_id = self.treeview.insert(
                parent_id, 'end', child.path, text=name,
                values=(checkbox, action_icon),
                open=child.open if hasattr(child, 'open') else False
            )

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
        '''Handle project selected path calling application layer and
        re-rendering items
        '''
        self.application.change_path(path)
        self.filetree = self.application.get()
        self.render_treeview()
        self.variables.reload()

    def select_configuration(self):
        '''Calls configuration path selector window to set
        the configuration path
        '''
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
        '''Handle configuration selected path calling application layer and
        re-rendering items
        '''
        self.application.change_configuration_path(path)
        ppath = self.filetree.path
        self.label['project']['text'] = ppath if ppath \
            else 'Selecione um diretório...'
        self.variables.reload()
        self.filetree = self.application.get()
        self.render_treeview()

    def add_template(self):
        '''Add a template inside selected node'''
        parent = self.node
        if self.application.configuration_path:
            parent.open = True
            child = self.template_application.create_child(
                parent, 'novotemplate.[ext]'
            )
            self.editor.show(child, True, self.render_treeview)
        else:
            messagebox.showwarning(
                'Atenção:',
                'Selecione onde salvar os templates primeiramente'
            )

        self.render_treeview()

    def add_configurable(self):
        '''Add configurable file'''
        if self.node:
            print('add configurable implementation pending')

    def open_file(self):
        '''Open file with templatizator editor window'''
        self.editor.show(self.node, False, self.render_treeview)

    def open_with(self):
        '''Open file with default OS editor'''
        OS.open_with(self.template_application.get_path(self.node))

    def remove_file(self):
        '''Remove file: template or configurable'''
        if messagebox.askyesno(
                'Pergunta:',
                'Deseja realmente remover o template?'
        ):
            self.template_application.remove(self.node)
            self.node.remove()
            self.filetree = self.application.get()

        self.render_treeview()

    def row_popup_selected(self, event):
        '''Call apropriated context menu when a treeview row is clicked with
        mouse right button click
        '''
        selected_path = self.treeview.identify_row(event.y)
        col = self.treeview.identify_column(event.x)
        # set selected node
        self.node = self.application.find_node(self.filetree, selected_path)

        if isinstance(self.node, Directory):
            self.directory_menu.post(event.x_root, event.y_root)
        elif col == '#0':
            self.file_menu.post(event.x_root, event.y_root)

    def row_selected(self, event):
        '''Call apropriated action when a treeview row is clicked,
        those action will be add, remove or edit template.
        When the action is add or edit the editor window is called.
        When remove action is called a confirmation dialog will be shown.
        '''
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
        col = self.treeview.identify_column(event.x)

        # add | remove
        if col == '#2':
            self.node = node
            # add
            if isinstance(node, Directory):
                self.add_template()
            # remove
            else:
                self.remove_file()
        # edit
        elif isinstance(node, File):
            self.node = node
            if col == '#1':
                self.node.save = not self.node.save
                if isinstance(node, Template):
                    self.template_application.save(self.node)
                self.render_treeview()
            else:
                self.open_file()

    # pylint: disable=unused-argument
    def row_opened(self, event):
        '''When project treeview directory is opened "save" the directory
        open state
        '''
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
        node.open = True
        icon = self.get_filetree_icon(node)
        text = f'{icon} {node.name}'
        self.treeview.item(selected_path, text=text)

    # pylint: disable=unused-argument
    def row_closed(self, event):
        '''When project treeview directory is closed "save" the directory
        open state
        '''
        selected_path = self.treeview.focus()
        node = self.application.find_node(self.filetree, selected_path)
        node.open = False
        icon = self.get_filetree_icon(node)
        text = f'{icon} {node.name}'
        self.treeview.item(selected_path, text=text)

    def before_show_tooltip(self, col, iid, tooltip):
        '''Decides wich tooltip message to show or if will show'''
        node = self.application.find_node(self.filetree, iid)
        if col == '#2' and isinstance(node, Directory):
            tooltip.text = 'Adicionar template'
            return True
        if col == '#2' and isinstance(node, File):
            tooltip.text = 'Remover'
            return True
        if col == '#1' and isinstance(node, File):
            tooltip.text = 'Salvar no projeto?'
            return True
        return False

    def save_templates(self):
        '''Call aplication layer to save the templates into the project folder.
        After the files are recorded asks user if he wants to open the project
        directory.
        It also shows a default error dialog if something goes wrong
        '''
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
        win.geometry(f'{width}x{height}+{x_orientation}+{y_orientation}')
