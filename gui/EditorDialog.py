from src.Configuration import configuration

class EditorDialog:
    def __init__(self, builder):
        self.dialog = builder.get_object('editor_toplevel')
        
        self.filename = builder.get_object('editor_filename_entry')
        self.editor = builder.get_object('editor_text')

        builder.get_object('editor_variable_combobox')#['command'] = self.variable_selected
        builder.get_object('editor_variable_button')['command'] = self.add_variable_to_template
        builder.get_object('editor_cancel_button')['command'] = self.cancel
        builder.get_object('editor_save_button')['command'] = self.save_template

    def add_variable(self, button):
        return None

    def variable_selected(self, combobox):
        return None

    def add_variable_to_template(self, button):
        return None

    def save_template(self, button):
        buff = self.editor.get_buffer()
        b = buff.get_bounds()

        filename = self.editor_filename_entry['text']
        configuration.save_template(self.node, filename, buff.get_text(b.start, b.end, True))
        self.cb()
        self.dialog.hide()

    def cancel(self, button):
        if self.is_new:
            self.node.remove()
        self.dialog.hide()
        self.cb()

    def show(self, node, is_new, cb):
        self.is_new = is_new
        self.node = node
        self.cb = cb
        self.elements.editor_filename_entry.set_text(self.node.name)

        buff = self.editor.get_buffer()
        buff.set_text(
            '' if is_new else configuration.get_template_content(node)
        )
        self.dialog.show()

