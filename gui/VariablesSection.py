from app import app

class VariablesSection:
    def __init__(self, elements):
        self.elements = elements

        self.name = self.elements.variable_name_entry
        self.value = self.elements.variable_value_entry
        self.action = self.elements.variable_action_button
        self.treeview = self.elements.variables_treeview
        self.store = self.elements.variables_liststore
        #self.store.clear()

        self.treeview.connect('row-activated', self.row_selected)
        self.action.connect('clicked', self.variable_action)
        self.row = None
        self.old_name = None

        self.treeview.set_activate_on_single_click(True)

    def variable_action(self, button):
        # add
        if not self.row:
            self.store.append([
                self.name.get_text(),
                self.value.get_text(),
                'x'
            ])
            app.configuration.add_variable(self.name.get_text(), self.value.get_text())
        # edit
        else:
            self.store[self.row][0] = self.name.get_text()
            self.store[self.row][1] = self.value.get_text()
            self.row = None
            self.action.set_label('+')
            app.configuration.change_variable(self.old_name, self.name.get_text(), self.value.get_text())

        self.name.set_text('')
        self.value.set_text('')

    def row_selected(self, treeview, row, col):
        # remove
        if col == self.elements.variable_actions_treeviewcolumn:
            self.store.remove(self.store[row].iter)
            app.configuration.remove_variable(self.store[row][0])
        # edit
        else:
            self.name.set_text(self.store[row][0])
            self.value.set_text(self.store[row][1])
            self.action.set_label('Salvar')
            self.row = row
            self.old_name = self.store[row][0]
