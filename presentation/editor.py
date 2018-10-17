'''Handler for editor window'''
from presentation.window import Window


# as a window handler it's necessary to record lots of attributes
# pylint: disable=too-many-instance-attributes
class Editor:
    '''Editor window class handler'''
    def __init__(self, builder, application, variable_application):
        self.application = application
        self.variable_application = variable_application

        self.node = None
        self.is_new = True
        self.last_selected = None
        self.call_back = None

        self.builder = builder

        self.dialog = None
        self.window = None
        self.filelabel = None
        self.filename = None
        self.editor = None
        self.combobox = None
        self.cancel_button = None
        self.save_button = None

        self.set_props()
        self.dialog.resizable(False, False)
        self.dialog.withdraw()

    def set_props(self):
        '''Set interface properties from builder obj'''
        builder = self.builder
        self.dialog = builder.get_object('editor_toplevel')
        self.window = builder.get_object('window')

        self.filelabel = builder.get_object('editor_filename_label')
        self.filename = builder.get_object('editor_filename_entry')
        self.editor = builder.get_object('editor_text')
        self.combobox = builder.get_object('editor_variable_combobox')

        self.cancel_button = builder.get_object('editor_cancel_button')
        self.save_button = builder.get_object('editor_save_button')

    def rebind(self):
        '''Rebind editor events'''
        self.set_props()

        self.save_button['command'] = self.save
        self.cancel_button['command'] = self.cancel

        self.combobox.bind('<<ComboboxSelected>>', self.variable_selected)
        self.filename.bind('<Button-1>', self.input_selected, self.filename)
        self.editor.bind('<Button-1>', self.input_selected, self.editor)

        self.dialog.protocol('WM_DELETE_WINDOW', self.cancel)

    def input_selected(self, event):
        '''Record filename entry as the last widget selected to add
        combobox variables selected
        '''
        self.last_selected = event.widget

    # argument required to call the event and not used by application
    # pylint: disable=unused-argument
    def variable_selected(self, event):
        '''Add variable selected in the combobox to the last widget selected'''
        var = f'[{self.combobox.get()}]'
        i = self.last_selected.index('insert')
        self.last_selected.insert(i, var)
        self.last_selected.focus_set()
        self.combobox.delete(0, 'end')

    def save(self):
        '''Save the template calling application layer and after call
        the callback passed from main window
        '''
        self.rebind()

        filename = self.filename.get()
        content = self.editor.get('1.0', 'end')

        # remove automatically tk added break line in the content
        content = content[0:-1]

        if self.is_new:
            self.node.name = filename
            self.application.add(self.node, content)
        else:
            self.application.save_file(
                self.node,
                filename,
                content
            )

        self.call_back()
        self.dialog.withdraw()

    def cancel(self):
        '''Cancel edition (or close the editor window): close the editor
        window and call callback passed from main window
        '''
        if self.is_new:
            self.node.remove()
        self.dialog.withdraw()
        self.call_back()

    def show(self, node, is_new, call_back):
        '''Show the editor window initiating edition cleaning the fields and
        recording (in memory) important data from file (as is_new and cb)
        '''
        self.rebind()

        self.is_new = is_new
        self.node = node
        self.call_back = call_back

        self.filename.delete(0, 'end')
        self.filename.insert(0, node.name)

        self.editor.delete('1.0', 'end')
        self.editor.insert(
            '1.0',
            '' if is_new else self.application.get(node)
        )

        self.combobox['values'] = list(map(
            lambda v: v.name, self.variable_application.get()
        ))

        self.dialog.transient(self.window)
        Window.center(self.dialog)
        self.dialog.deiconify()

        if is_new:
            self.last_selected = self.filename
            self.filename.select_range(0, 'end')
            self.filename.icursor(0)
        else:
            self.last_selected = self.editor
            self.editor.mark_set('insert', '1.0')

        self.last_selected.focus_set()
