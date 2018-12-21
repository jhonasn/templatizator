'''Handler for editor window'''
from copy import copy
from difflib import SequenceMatcher
from tkinter.ttk import Checkbutton
from presentation.window import Window
from domain.model import Template


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
        self.original_text = None
        self.template_lines = []
        self.templates = []

        self.window = builder.get_object('window_toplevel')
        self.dialog = builder.get_object('configurable_toplevel')
        self.editor = builder.get_object('configurable_editor_text')
        self.combobox = builder.get_object('configurable_variable_combobox')
        self.add_template_button = builder.get_object('add_template_button')
        cancel_button = builder.get_object('configurable_cancel_button')
        save_button = builder.get_object('configurable_save_button')
        template_frame = builder.get_object('template_labelframe')

        self.add_template_button['command'] = self.add_template
        cancel_button['command'] = self.cancel
        save_button['command'] = self.save
        self.combobox.bind('<<ComboboxSelected>>', self.variable_selected)
        self.editor.bind('<KeyRelease>', self.key_pressed)
        self.editor.bind('<Key>', self.key_press)
        self.editor.bind('<ButtonRelease-1>', self.editor_cursor_changed)
        self.dialog.protocol('WM_DELETE_WINDOW', self.cancel)

        self.dialog.resizable(False, False)
        self.dialog.withdraw()

        all_templates = self.template_application.get_all()
        select_all_template = Template()
        select_all_template.name = 'Todos'
        all_templates.insert(0, select_all_template)
        for index, template in enumerate(all_templates):
            row, col = int(index / 3), index % 3
            check = Checkbutton(template_frame, name=str(index),
                                text=template.name)
            # deselect checkbox
            check.invoke()
            check.invoke()
            if (index == 0):
                check['command'] = self.checkbox_all_selected

            check.grid(row=row, column=col)
            self.templates.append(check)
            check.grid_forget()

    def paint(self):
        '''Paints the template lines'''
        content = self.editor.get('1.0', 'end')[0:-1]
        sequence = SequenceMatcher(None, self.original_text, content)

        self.editor.tag_delete('template')

        # pylint: disable=invalid-name, unused-variable
        for tag, o1, o2, c1, c2 in sequence.get_opcodes():
            if tag == 'insert':
                start, end = f'1.0+{c1}c', f'1.0+{c2}c'
                self.editor.tag_add('template', start, end)
                self.editor.tag_config('template', background='lightgreen')

    @property
    def current_line(self):
        '''Return currente line in the text editor'''
        cursor = self.editor.index('insert')
        return int(float(cursor))

    # pylint: disable=unused-argument
    def key_press(self, event):
        '''Block the user to edit original file content'''
        next_char = self.editor.get('insert', 'insert+1c')
        # allow navigation keys
        if event.keysym in ['Left', 'Right', 'Up', 'Down', 'Home', 'End']:
            return None
        # block
        if self.current_line not in self.template_lines:
            return 'break'
        # block, prevent join template lines with template content
        if event.keysym == 'Delete' and next_char == '\n':
            return 'break'
        if event.keysym == 'Return':
            self.template_lines.append(self.current_line + 1)
        return None

    # pylint: disable=unused-argument
    def change_template_options(self):
        '''Show/hide template options'''
        if self.current_line in self.template_lines:
            self.add_template_button.grid_forget()
            for index, check in enumerate(self.templates):
                row, col = int(index / 3), index % 3
                check.grid(row=row, column=col)
        else:
            self.add_template_button.grid(row=0, column=0, sticky='e')
            for check in self.templates:
                check.grid_forget()

    def editor_cursor_changed(self, event):
        '''Mouse click editor cursor changed event handler'''
        self.change_template_options()

    def key_pressed(self, event):
        '''Update editor painted lines and template control when key is pressed
        '''
        self.paint()
        # show/hide template line options
        if event.keysym in ['Up', 'Down']:
            self.change_template_options()

    def checkbox_all_selected(self):
        '''Verify if all checkbutton was selected'''
        print('is checkbox all selected?', 'selected' in self.templates[0].state())


    def add_template(self):
        '''Add a template line and show template options'''
        cursor = self.editor.index('insert lineend')
        self.editor.insert(cursor, '\n')
        self.editor.mark_set('insert', cursor + '+1c')
        self.editor.focus_set()
        cursor = self.editor.index('insert')

        self.template_lines.append(int(float(cursor)))

        self.paint()

        self.change_template_options()

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
        if self.is_new:
            self.application.add(self.node)
        else:
            self.application.save(self.node)

        self.call_back()
        self.dialog.withdraw()

    def show(self, node, is_new, call_back):
        '''Show the editor window initiating edition cleaning the fields and
        recording (in memory) important data from file (as is_new and cb)
        '''
        self.is_new = is_new
        self.node = node
        self.call_back = call_back

        self.original_text = self.application.get(node)
        self.editor.delete('1.0', 'end')
        self.editor.insert(
            '1.0', self.original_text
        )

        self.combobox['values'] = ['template.name', 'template.path'] + list(
            map(
                lambda v: v.name, self.variable_application.get()
            ))

        self.dialog.transient(self.window)
        self.dialog.deiconify()

        self.editor.mark_set('insert', '1.0')
        self.editor.focus_set()

        self.change_template_options()
