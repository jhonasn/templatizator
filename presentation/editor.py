#from src.Configuration import configuration
from presentation.application import builder

class Editor:
    def __init__(self):
        self.dialog = builder.get_object('editor_toplevel')
        #self.window = builder.get_object('window')
        self.dialog.resizable(False, False)
        
        self.filename = builder.get_object('editor_filename_entry')
        self.editor = builder.get_object('editor_text')
        self.combobox = builder.get_object('editor_variable_combobox')

        builder.get_object('editor_cancel_button')['command'] = self.cancel
        builder.get_object('editor_save_button')['command'] = self.save_template
        self.combobox.bind('<<ComboboxSelected>>', self.variable_selected)
        self.filename.bind('<Button-1>', self.input_selected, self.filename)
        self.editor.bind('<Button-1>', self.input_selected, self.editor)

        self.dialog.withdraw()
        self.dialog.protocol('WM_DELETE_WINDOW', self.cancel)

    def input_selected(self, event):
        self.last_selected = event.widget

    def variable_selected(self, event):
        var = f'[{self.combobox.get()}]'
        i = self.last_selected.index('insert')
        self.last_selected.insert(i, var)
        self.last_selected.focus_set()
        self.combobox.delete(0, 'end')

    def save_template(self):
        filename = self.filename.get()
        configuration.save_template(
            self.node,
            filename,
            self.editor.get('1.0', 'end')
        )
        self.cb()
        self.dialog.withdraw()

    def cancel(self):
        if self.is_new:
            self.node.remove()
        self.dialog.withdraw()
        self.cb()

    def show(self, node, is_new, cb):
        self.is_new = is_new
        self.node = node
        self.cb = cb

        self.filename.delete(0, 'end')
        self.filename.insert(0, node.name)

        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0',
            '' if is_new else configuration.get_template_content(node)
        )

        self.combobox['values'] = list(configuration.get_variables())

        self.dialog.deiconify()
        #self.dialog.transient(self.window)

        if is_new:
            self.last_selected = self.filename
            self.filename.select_range(0, 'end')
            self.filename.icursor(0)
        else:
            self.last_selected = self.editor
            self.editor.mark_set('insert', '1.0')

        self.last_selected.focus_set()

