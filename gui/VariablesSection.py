from app import app

class VariablesSection:
    def __init__(self, elements):
        self.elements = elements

        self.name = self.elements.variable_name_entry
        self.value = self.elements.variable_value_entry
        self.action = self.elements.variable_action_button
        self.cancel = self.elements.variable_cancel_button
        self.treeview = self.elements.variables_treeview
        self.store = self.elements.variables_liststore

        for key, value in app.configuration.get_variables():
            self.store.append([key, value, 'x'])

        self.treeview.connect('row-activated', self.row_selected)
        self.action.connect('clicked', self.variable_action)
        self.cancel.connect('clicked', self.cancel_action)
        self.row = None
        self.old_name = None

        self.treeview.set_activate_on_single_click(True)

    def variable_action(self, button):
        name = self.name.get_text()
        value = self.value.get_text()

        if not name or not value:
            self.elements.alert('Preencha o nome e o valor da variavel')
            return

        # add
        if not self.row:
            self.store.append([name, value, 'x'])
            app.configuration.add_variable(name, value)
        # edit
        else:
            self.store[self.row][0] = name
            self.store[self.row][1] = value
            self.row = None
            self.action.set_label('+')
            app.configuration.change_variable(self.old_name, name, value)

        self.cancel_action(None)

    def row_selected(self, treeview, row, col):
        # remove
        if col == self.elements.variables_actions_treeviewcolumn:
            app.configuration.remove_variable(self.store[row][0])
            self.store.remove(self.store[row].iter)
        # edit
        else:
            self.name.set_text(self.store[row][0])
            self.value.set_text(self.store[row][1])
            self.action.set_label('Salvar')
            self.row = row
            self.old_name = self.store[row][0]

    def cancel_action(self, button):
        self.row = None
        self.name.set_text('')
        self.value.set_text('')

