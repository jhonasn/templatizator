'''Handler for cofigurable editor window'''
from copy import copy
from templatizator.locales.i18n import _
from templatizator.domain.domain import Template


# as a window handler it's necessary to record lots of attributes
# pylint: disable=too-many-instance-attributes
class ConfigurableEditor:
    '''Configurable editor window class handler'''
    # pylint: disable=too-many-locals
    def __init__(self, builder, application, variable_application,
                 template_application):
        self.application = application
        self.variable_application = variable_application
        self.template_application = template_application

        self.is_new = None
        self.node = None
        self.call_back = None

        self.window = builder.get_object('window_toplevel')
        self.dialog = builder.get_object('configurable_toplevel')
        self.editor = builder.get_object('configurable_editor_text')
        self.combobox = builder.get_object('configurable_variable_combobox')
        cancel_button = builder.get_object('configurable_cancel_button')
        save_button = builder.get_object('configurable_save_button')

        # translate labels
        self.dialog.title(_('[Templatizator] Configurable file editing'))
        builder.get_object('configurable_variable_label')['text'] = _(
            'Add variable:')
        cancel_button['text'] = _('Cancel')
        save_button['text'] = _('Save')

        cancel_button['command'] = self.cancel
        save_button['command'] = self.save
        self.combobox.bind('<<ComboboxSelected>>', self.variable_selected)
        self.dialog.protocol('WM_DELETE_WINDOW', self.cancel)

        self.dialog.resizable(False, False)
        self.dialog.withdraw()

    # argument required to call the event and not used by application
    # pylint: disable=unused-argument
    def variable_selected(self, event):
        '''Add variable selected in the combobox to the last widget selected'''
        var = f'[{self.combobox.get()}]'
        i = self.editor.index('insert')
        self.editor.insert(i, var)
        self.editor.focus_set()
        self.combobox.delete(0, 'end')

    def cancel(self):
        '''Cancel edition (or close the editor window): close the editor
        window and call callback passed from main window
        '''
        if self.is_new:
            self.node.remove()
        self.dialog.withdraw()
        self.call_back()

    def save(self):
        '''Save the configurable calling application layer and after call
        the callback passed from main window
        '''
        content = self.editor.get('1.0', 'end')

        # remove automatically tk added break line in the content
        content = content[0:-1]
        if self.is_new:
            self.application.add(self.node, content)
        else:
            self.application.save_file(self.node, None, content)

        self.call_back()
        self.dialog.withdraw()

    def show(self, node, is_new, call_back):
        '''Show the editor window initiating edition cleaning the fields and
        recording (in memory) important data from file (as is_new and cb)
        '''
        self.is_new = is_new
        self.node = node
        self.call_back = call_back

        self.editor.delete('1.0', 'end')
        self.editor.insert(
            '1.0', self.application.get(node)
        )

        all_templates = self.template_application.get_all()
        select_all_template = Template()
        select_all_template.name = 'All'
        all_templates.insert(0, select_all_template)

        for index, template in enumerate(copy(all_templates)):
            name = template.name
            template_path = copy(template)
            template_path.name += '.path'
            template.name += '.name'

            all_templates.insert(index * 2 + 1, template_path)

            # add relative_path to All template
            is_template_all = name == 'All'
            if is_template_all:
                template_relpath = copy(template)
                template_relpath.name = f'{name}.relative_path'
                all_templates.insert(index * 2 + 2, template_relpath)

        self.combobox['values'] = list(map(
            lambda v: v.name, self.variable_application.get()
        )) + list(map(
            lambda t: 'template.' + t.name, all_templates
        ))

        self.dialog.transient(self.window)
        self.dialog.deiconify()

        self.editor.mark_set('insert', '1.0')
        self.editor.focus_set()
