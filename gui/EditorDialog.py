class EditorDialog:
    def __init__(self, elements):
        self.elements = elements

        self.dialog = self.elements.editor_dialog
        self.editor = self.elements.editor_textview

        self.elements.variables_combobox.connect('changed', self.variable_selected)
        self.elements.add_variable_button.connect('clicked', self.add_variable_to_template)
        self.elements.cancel_button.connect('clicked', self.cancel)
        self.elements.save_button.connect('clicked', self.save_template)

        self.dialog.set_transient_for(self.elements.window)

    def add_variable(self, button):
        return None

    def variable_selected(self, combobox):
        return None

    def add_variable_to_template(self, button):
        return None

    def save_template(self, button):
        return None

    def cancel(self, button):
        if self.node.is_new:
            self.node.remove()
        self.dialog.hide()
        self.cb()

    def show(self, node, cb):
        self.node = node
        self.cb = cb
        self.elements.editor_filename_entry.set_text(self.node.name)
        self.dialog.show()
