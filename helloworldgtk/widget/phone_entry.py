import gi
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class PhoneEntry(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Digite o número de telefone")
        self.entry.set_max_length(11)  # Define o limite máximo de entrada
        self.entry.connect("changed", self.on_entry_changed)
        
        self.label = Gtk.Label()
        self.label.set_halign(Gtk.Align.END)
        self.label.set_valign(Gtk.Align.END)
        
        self.pack_start(self.entry, False, False, 0)
        self.pack_start(self.label, False, False, 0)
    
    def on_entry_changed(self, widget):
        text = re.sub("[^0-9]", "", self.entry.get_text())  # Remove caracteres não numéricos
        text = text[:11]  # Limita a entrada a 11 caracteres
        formatted_text = self.format_phone(text)
        self.label.set_markup(f"<span font='8'>{formatted_text}</span>")  # Usa Pango markup para definir o tamanho da fonte

    def format_phone(self, phone):
        formatted = "".join(phone)
        if len(phone) == 11:  # Celular com 9 dígitos
            formatted = f"({phone[:2]}) {phone[2]} {phone[3:7]}-{phone[7:]}"
        elif len(phone) == 10:  # Telefone fixo com 8 dígitos
            formatted = f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
        elif len(phone) > 6:
            formatted = f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
        elif len(phone) > 2:
            formatted = f"({phone[:2]}) {phone[2:]}"
        elif len(phone) > 1:
            formatted = f"({phone[:2]})"
        else:
            formatted = f"{phone}"  # Exibe o começo da formatação
        
        return formatted

class PhoneFormatter(Gtk.Window):
    def __init__(self):
        super().__init__(title="Phone Formatter")
        self.set_border_width(10)
        self.set_default_size(300, 100)

        vbox = Gtk.VBox(spacing=2)  # Reduzindo o espaçamento para aproximar os widgets
        self.add(vbox)

        self.entry_widget = PhoneEntry()
        vbox.pack_start(self.entry_widget, False, False, 0)

if __name__ == "__main__":
    app = PhoneFormatter()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
