import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class GuiHandler:
    def __init__(self):
        self.gtk = Gtk
        self.builder = self.gtk.Builder()

        self.builder.add_from_file('./gui/main-gui.glade')

        self.window = self.builder.get_object('window')
        self.treeview = self.builder.get_object('destination_treeview')
        
        self.editor_dialog = self.builder.get_object('editor_dialog')
        self.editor = self.builder.get_object('editor_textview')

        self.builder.connect_signals({
            'on_variables_button_clicked': self.open_variables_dialog,
            'on_destination_filechooserbutton_file_set': self.destination_selected,
            'on_configuration_filechooserbutton_file_set': self.configuration_selected,
            
            'on_variables_combobox_changed': self.variable_selected,
            'on_add_variable_button_clicked': self.add_variable_to_template,
            'on_cancel_button_clicked': self.editor_dialog.hide,
            'on_save_button_clicked': self.save_template
        })

        self.editor_dialog.set_transient_for(self.window)

        self.window.show_all()

        self.window.connect('destroy', self.gtk.main_quit)

    def open_variables_dialog(self, button):
        #self.detalhes_dialog.show()

    def destination_selected(self, file_chooser):
        uri = file_chooser.get_uri()
        #mount estructure on treeview
        for r, d, f in os.walk(uri):
            for dir in d:
                self.treeview_store.append
        
    def configuration_selected(self, file_chooser):
        return None

    def variable_selected(self, combobox):
        return None

    def add_variable_to_template(self, button):
        return None

    def save_template(self, button):
        return None

    def start(self):
        Gtk.main()
