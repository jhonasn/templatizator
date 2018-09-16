from app import app

class EditorDialog:
    def __init__(self, elements):
        self.elements = elements

        self.dialog = self.elements.editor_dialog
        self.editor = self.elements.editor_textview

        self.elements.editor_variable_combobox.connect('changed', self.variable_selected)
        self.elements.editor_variable_add_button.connect('clicked', self.add_variable_to_template)
        self.elements.editor_cancel_button.connect('clicked', self.cancel)
        self.elements.editor_save_button.connect('clicked', self.save_template)

        self.dialog.set_transient_for(self.elements.window)

    def add_variable(self, button):
        return None

    def variable_selected(self, combobox):
        return None

    def add_variable_to_template(self, button):
        return None

    def save_template(self, button):
        buff = self.editor.get_buffer()
        b = buff.get_bounds()

        filename = self.elements.editor_filename_entry.get_text()
        app.configuration.save_template(self.node, filename, buff.get_text(b.start, b.end, True))
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
            '' if is_new else app.configuration.get_template_content(node)
        )
        self.dialog.show()

