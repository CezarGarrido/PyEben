import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class FormValidator():
    def __init__(self):
        self.fields = []  # Lista para armazenar os campos do formulário

    def add(self, label_text, validation_func=None, format_func=None):
        field = FormField(label_text, validation_func, format_func)
        self.fields.append(field)
        return field
        
    def validate_all(self):
        all_valid = True
        for field in self.fields:
            if not field.validate():
                print("invalido {}", field.label.get_text())
                all_valid = False
        return all_valid
    
    def get_values(self):
        return {field.label.get_text(): field.get_text() for field in self.fields}


class FormField(Gtk.Box):
    def __init__(self, label_text, validation_func=None, format_func=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.validation_func = validation_func
        self.format_func = format_func

        # Label superior com o nome do campo
        self.label = Gtk.Label(label=label_text, xalign=0)
        
        # Campo de entrada
        self.entry = Gtk.Entry()
        self.entry.connect("changed", self.validate)
        
        # Label de erro
        self.error_label = Gtk.Label(label="", xalign=0)
        self.error_label.get_style_context().add_class("error_label")
        self.error_label.set_no_show_all(True)

        # Label de formatação
        self.formatted_label = Gtk.Label(label="", xalign=0)
        self.formatted_label.get_style_context().add_class("formatted_label")
        self.formatted_label.set_no_show_all(True)
        
        # Layout
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(self.label, True, True, 0)
        hbox.pack_end(self.formatted_label, False, False, 0)

        self.pack_start(hbox, False, False, 0)
        self.pack_start(self.entry, False, False, 0)
        self.pack_start(self.error_label, False, False, 0)
        
        self.load_css()
    
    def load_css(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        .entry_error {
            border: 2px solid red;
            background-color: #ffe6e6;
        }
        .error_label {
            color: red;
            font-size: 12px;
            font-weight: bold;
        }
        .formatted_label {
            color: #007bff;
            font-size: 12px;
            font-style: italic;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def set_text(self, text):
        if text == None:
            return
        self.entry.set_text(text)
    
    def validate(self, widget=None):
        text = self.entry.get_text().strip()
        
        # Aplicar formatação
        if self.format_func:
            formatted_text = self.format_func(text)
            if formatted_text == "":
                self.formatted_label.set_text("")
                self.formatted_label.hide()
            else:
                self.formatted_label.set_text(f"📌 {formatted_text}")
                self.formatted_label.show()
        
        # Aplicar validação
        if self.validation_func:
            error_message = self.validation_func(text)
            print("error message {}", error_message)
            if error_message:
                self.error_label.set_text(error_message)
                self.error_label.show()
                self.entry.get_style_context().add_class("entry_error")
                return False
            else:
                self.error_label.hide()
                self.entry.get_style_context().remove_class("entry_error")
        return True
    
    def get_text(self):
        return self.entry.get_text().strip()
    
    def is_valid(self):
        return not self.error_label.get_visible()
