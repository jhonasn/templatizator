class VariablesDialog:
    def __init__(self, elements):
        self.elements = elements
        
        self.dialog = self.elements.variables_dialog
        self.treeview = self.elements.variables_treeview
        self.store = self.elements.variables_liststore
        self.store.append(['var tal', '1', None])

        self.elements.add_variable_button.connect('clicked', self.add_variable)

        self.dialog.set_transient_for(self.elements.window)

    def add_variable(self, button):
        print('Add var var')
        print('Add var ' + self.elements.variable_name_entry.get_text() + ':' + self.elements.variable_value_entry.get_text())

    def show(self, button):
        self.dialog.show()
