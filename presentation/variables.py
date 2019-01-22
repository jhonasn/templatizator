'''Handler for variables section into the main window'''
from tkinter import messagebox
from domain.infrastructure import ProjectNotSetWarning
from presentation.helper import get_tkinter_unicode, is_unicode_available
from presentation.widgets import Tooltip
from locales.translation import _

icons = is_unicode_available('💾')
ADD_ICON = get_tkinter_unicode('➕')
REMOVE_ICON = get_tkinter_unicode('❌')
SAVE_ICON = get_tkinter_unicode('💾' if icons else '✔')


# as a window section handler it's necessary to record lots of attributes
# pylint: disable=too-many-instance-attributes
class Variables:
    '''Variables section class handler'''
    def __init__(self, builder, application):
        self.application = application

        self.name = builder.get_object('variable_name_entry')
        self.value = builder.get_object('variable_value_entry')
        self.action = builder.get_object('variable_action_button')
        self.cancel = builder.get_object('variable_cancel_button')
        self.treeview = builder.get_object('variables_treeview')
        self.action_tooltip = Tooltip(self.action, _('Add'))
        Tooltip(self.cancel, _('Cancel'))
        Tooltip(self.treeview, _('Remove'), col='#3')

        # translate labels
        builder.get_object('variable_name_label')['text'] = _('Name:')
        builder.get_object('variable_value_label')['text'] = _('Value:')
        self.treeview.heading('variable_name_treeviewcolumn', text=_('Name'))
        self.treeview.heading('variable_value_treeviewcolumn', text=_('Value'))

        self.treeview.bind('<ButtonRelease-1>', self.row_selected)
        self.action['command'] = self.variable_action
        self.cancel['command'] = self.cancel_action
        self.row = None
        self.old_name = None

        self.reload()

    def reload(self):
        '''reload variables into the reeview'''
        self.treeview.delete(*self.treeview.get_children())

        for var in self.application.get():
            self.treeview.insert('', 'end', values=(var.name, var.value,
                                                    REMOVE_ICON))

    @staticmethod
    def set_entry_text(entry, text):
        '''replace entry text by the text passed'''
        entry.delete(0, 'end')
        entry.insert(0, text)

    def variable_action(self):
        '''Add or save edition when add/save button is clicked'''
        name = self.name.get()
        value = self.value.get()
        selected_id = self.treeview.focus()

        if not name or not value:
            messagebox.showwarning(
                _('Warning'),
                _('Fill variable name and value')
            )
            return

        # add
        if not self.row:
            try:
                self.application.add(name, value)
                self.treeview.insert('', 'end', values=(name, value,
                                                        REMOVE_ICON))
            except ProjectNotSetWarning:
                messagebox.showwarning(
                    _('Warning'),
                    _('Select a project first')
                )
        # edit
        else:
            self.treeview.item(selected_id, values=(name, value,
                                                    REMOVE_ICON))
            self.application.change(self.old_name, name, value)

        self.cancel_action()

    def row_selected(self, event):
        '''Select to edit or delete variable according column clicked'''
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
            Variables.set_entry_text(self.name, row_name)
            Variables.set_entry_text(self.value, row_value)
            self.action['text'] = SAVE_ICON
            self.action_tooltip.text = _('Save')
            self.row = selected_id
            self.old_name = row_name

    def cancel_action(self):
        '''Cancel variable edition cleaning name and value entries'''
        self.row = None
        self.old_name = None
        self.action['text'] = ADD_ICON
        self.name.delete(0, 'end')
        self.value.delete(0, 'end')
