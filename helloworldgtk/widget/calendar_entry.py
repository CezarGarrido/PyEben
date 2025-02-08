import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class GtkFormValidator:
    def __init__(self, grid):
        self.entries = {}
        self.validators = {}
        self.error_labels = {}
        self.grid = grid
        self.row_counter = 0
    
    def add(self, label_text, validator):
        label = Gtk.Label(label=label_text, xalign=0)
        entry = Gtk.Entry()
        error_label = Gtk.Label(label="", xalign=0)
        error_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("red"))
        
        self.entries[entry] = validator
        self.error_labels[entry] = error_label
        entry.connect("changed", self.validate_field, entry)
        
        self.grid.attach(label, 0, self.row_counter, 1, 1)
        self.grid.attach(entry, 1, self.row_counter, 1, 1)
        self.grid.attach(error_label, 1, self.row_counter + 1, 1, 1)
        
        self.row_counter += 2
    
    def validate_field(self, entry, _):
        text = entry.get_text().strip()
        validator = self.entries[entry]
        result = validator(text)
        
        if isinstance(result, tuple):
            is_valid, error_message = result
        else:
            is_valid, error_message = result, ""
        
        self.set_entry_style(entry, is_valid)
        self.error_labels[entry].set_text(error_message if not is_valid else "")
        return is_valid
    
    def validate_all(self, _):
        all_valid = True
        for entry in self.entries:
            if not self.validate_field(entry, None):
                all_valid = False
    
    def set_entry_style(self, entry, is_valid):
        if is_valid:
            entry.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        else:
            entry.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 0.8, 0.8, 1))

if __name__ == "__main__":
    def validate_name(text):
        if len(text) <= 2:
            return False, "Nome deve ter mais de 2 caracteres."
        return True
    
    def validate_email(text):
        if "@" not in text or "." not in text:
            return False, "Email inválido."
        return True
    
    def validate_age(text):
        if not text.isdigit() or not (0 < int(text) < 120):
            return False, "Idade deve ser um número entre 1 e 119."
        return True
    
    window = Gtk.Window(title="Validador de Formulário")
    window.set_default_size(400, 300)
    
    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    grid.set_column_spacing(10)
    grid.set_border_width(10)
    
    form_validator = GtkFormValidator(grid)
    
    form_validator.add("Nome", validate_name)
    form_validator.add("Email", validate_email)
    form_validator.add("Idade", validate_age)
    
    submit_button = Gtk.Button(label="Validar")
    submit_button.connect("clicked", form_validator.validate_all)
    grid.attach(submit_button, 0, form_validator.row_counter, 2, 1)
    
    window.add(grid)
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
