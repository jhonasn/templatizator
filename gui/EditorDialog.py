from src.Configuration import configuration

class EditorDialog:
    def __init__(self, builder):
        self.dialog = builder.get_object('editor_toplevel')
        #self.window = builder.get_object('window')
        
        self.filename = builder.get_object('editor_filename_entry')
        self.editor = builder.get_object('editor_text')

        builder.get_object('editor_variable_combobox')#['command'] = self.variable_selected
        builder.get_object('editor_variable_button')['command'] = self.add_variable_to_template
        builder.get_object('editor_cancel_button')['command'] = self.cancel
        builder.get_object('editor_save_button')['command'] = self.save_template

        self.dialog.withdraw()
        self.dialog.protocol('WM_DELETE_WINDOW', self.cancel)

    def add_variable(self):
        return None

    def variable_selected(self):
        return None

    def add_variable_to_template(self):
        return None

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

        self.dialog.deiconify()
        #self.dialog.transient(self.window)

