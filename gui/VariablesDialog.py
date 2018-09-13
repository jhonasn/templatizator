class VariablesDialog:
    def __init__(self, elements):
        self.elements = elements

        self.dialog = self.elements.variables_dialog
        self.treeview = self.elements.variables_treeview
        self.store = self.elements.variables_liststore
        #self.store.clear()

        self.treeview.connect('row-activated', self.remove_row)
        self.elements.variables_add_button.connect('clicked', self.add_variable)
        self.dialog.connect('delete-event', self.close)

        self.dialog.set_transient_for(self.elements.window)
        self.treeview.set_activate_on_single_click(True)

    def add_variable(self, button):
        self.store.append([
            self.elements.variable_name_entry.get_text(),
            self.elements.variable_value_entry.get_text(),
            u'⌧'#🗑
        ])

    def remove_row(self, treeview, row, col):
        if col == self.elements.variable_actions_treeviewcolumn:
            self.store.remove(self.store[row].iter)

    def show(self, button):
        self.dialog.show()

    def close(self, button, w):
        self.dialog.hide()
        return True
