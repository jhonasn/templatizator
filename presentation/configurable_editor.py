'''Handler for editor window'''
from difflib import SequenceMatcher
from presentation.window import Window
from presentation.editor import Editor


# as a window handler it's necessary to record lots of attributes
# pylint: disable=too-many-instance-attributes
class ConfigurableEditor(Editor):
    '''Configurable editor window class handler'''
    def __init__(self, builder, application, variable_application):
        super().__init__(builder, application, variable_application)
        self.original_text = None
        self.current_text = None

    def rebind(self):
        '''Rebind editor events'''
        super().set_props()

        self.cancel_button['command'] = self.cancel
        self.save_button['command'] = self.save
        self.combobox.bind('<<ComboboxSelected>>', self.variable_selected)
        self.editor.bind('<KeyRelease>', self.key_pressed)

        # hide file name
        self.filelabel.grid_forget()
        self.filename.grid_forget()

        self.dialog.protocol('WM_DELETE_WINDOW', self.cancel)

    # pylint: disable=unused-argument
    def key_pressed(self, event):
        '''Updates the UI and get separate template lines
        when key is pressed
        '''
        content = self.editor.get('1.0', 'end')[0:-1]
        sequence = SequenceMatcher(None, self.original_text, content)

        tags = [tag for tag, o1, o2, c1, c2 in sequence.get_opcodes()]
        reseted = False
        if 'replace' in tags or 'delete' in tags:
            cursor = self.editor.index('insert')
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', self.current_text)
            self.editor.mark_set('insert', cursor)
            reseted = True
            sequence = SequenceMatcher(None, self.original_text,
                                       self.current_text)

        self.editor.tag_delete('template')
        template_lines = []

        # pylint: disable=invalid-name, unused-variable
        for tag, o1, o2, c1, c2 in sequence.get_opcodes():
            if tag == 'insert':
                start, end = f'1.0+{c1}c', f'1.0+{c2}c'
                self.editor.tag_add('template', start, end)
                self.editor.tag_config('template', background='lightgreen')

                template_lines.append(content[c1:c2])

        if not reseted:
            self.current_text = content

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
        '''Closes the editor window but execute some tasks before'''
        # re-show file name
        self.filelabel.grid(row=0, column=0, sticky='w')
        self.filename.grid(row=0, column=1, sticky='ew')
        super().cancel()

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
        self.rebind()
        self.is_new = is_new
        self.node = node
        self.call_back = call_back

        self.current_text = self.original_text = self.application.get(node)
        self.editor.delete('1.0', 'end')
        self.editor.insert(
            '1.0', self.original_text
        )

        self.combobox['values'] = ['template.name', 'template.path'] + list(
            map(
                lambda v: v.name, self.variable_application.get()
            ))

        self.dialog.transient(self.window)
        Window.center(self.dialog)
        self.dialog.deiconify()

        self.editor.mark_set('insert', '1.0')
        self.editor.focus_set()
