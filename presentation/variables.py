from tkinter import messagebox
from domain.infrastructure import ProjectNotSetWarning

class Variables:
    def __init__(self, builder, application):
        self.application = application

        self.name = builder.get_object('variable_name_entry')
        self.value = builder.get_object('variable_value_entry')
        self.action = builder.get_object('variable_action_button')
        self.cancel = builder.get_object('variable_cancel_button')
        self.treeview = builder.get_object('variables_treeview')

        self.treeview.bind('<ButtonRelease-1>', self.row_selected)
        self.action['command'] = self.variable_action
        self.cancel['command'] = self.cancel_action
        self.row = None
        self.old_name = None

        self.reload()

    def reload(self):
        self.treeview.delete(*self.treeview.get_children())

        for var in self.application.get():
            self.treeview.insert('', 'end', values=[var.name, var.value, '❌'])

    def set_entry_text(self, entry, text):
        entry.delete(0, 'end')
        entry.insert(0, text)

    def variable_action(self):
        name = self.name.get()
        value = self.value.get()
        selected_id = self.treeview.focus()
        item = self.treeview.item(selected_id)

        if not name or not value:
            messagebox.showwarning(
                'Atenção:',
                'Preencha o nome e o valor da variavel'
            )
            return

        # add
        if not self.row:
            try:
                self.application.add(name, value)
                self.treeview.insert('', 'end', values=[name, value, '❌'])
            except ProjectNotSetWarning:
                messagebox.showwarning(
                    'Atenção:',
                    'Selecione um projeto primeiramente'
                )
        # edit
        else:
            self.treeview.item(selected_id, values=[name, value, '❌'])
            self.application.change(self.old_name, name, value)

        self.cancel_action()

    def row_selected(self, event):
        selected_id = self.treeview.focus()
        item = self.treeview.item(selected_id)
        col = self.treeview.identify_column(event.x)

        row_name = item['values'][0]
        row_value = item['values'][1]

        # remove
        if col == '#3':
            self.application.remove(row_name)
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

