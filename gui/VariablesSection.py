from tkinter import messagebox

from src.Configuration import configuration

class VariablesSection:
    def __init__(self, builder):
        self.name = builder.get_object('variable_name_entry')
        self.value = builder.get_object('variable_value_entry')
        self.action = builder.get_object('variable_action_button')
        self.cancel = builder.get_object('variable_cancel_button')
        self.treeview = builder.get_object('variables_treeview')

        self.reload()

        self.treeview.bind('<ButtonRelease-1>', self.row_selected)
        self.action['command'] = self.variable_action
        self.cancel['command'] = self.cancel_action
        self.row = None
        self.old_name = None

    def reload(self):
        self.treeview.delete(*self.treeview.get_children())

        for key, value in configuration.get_variables().items():
            self.treeview.insert('', 'end', values=[key, value, '❌'])

    def set_entry_text(self, entry, text):
        entry.delete(0, 'end')
        entry.insert(0, text)

    def variable_action(self):
        name = self.name.get()
        value = self.value.get()
        selected_id = self.treeview.focus()
        item = self.treeview.item(selected_id)

        if not name or not value:
            messagebox.showwarning('Atenção:', 'Preencha o nome e o valor da variavel')
            return

        # add
        if not self.row:
            self.treeview.insert('', 'end', values=[name, value, '❌'])
            configuration.add_variable(name, value)
        # edit
        else:
            self.treeview.item(selected_id, values=[name, value, '❌'])
            configuration.change_variable(self.old_name, name, value)

        self.cancel_action()

    def row_selected(self, event):
        selected_id = self.treeview.focus()
        item = self.treeview.item(selected_id)
        col = self.treeview.identify_column(event.x)

        row_name = item['values'][0]
        row_value = item['values'][1]

        # remove
        if col == '#3':
            configuration.remove_variable(row_name)
            self.treeview.delete(selected_id)
        # edit
        else:
            self.set_entry_text(self.name, row_name)
            self.set_entry_text(self.value, row_value)
            self.action['text'] = '✓'
            self.row = selected_id
            self.old_name = row_name

    def cancel_action(self):
        self.row = None
        self.old_name = None
        self.action['text'] = '➕'
        self.name.delete(0, 'end')
        self.value.delete(0, 'end')

