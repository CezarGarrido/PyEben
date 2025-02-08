import gi
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class CPFEntry(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Digite o número de telefone")
        self.entry.set_max_length(14)  # Define o limite máximo de entrada
        self.entry.connect("changed", self.on_entry_changed)
        
        self.label = Gtk.Label()
        self.label.set_halign(Gtk.Align.END)
        self.label.set_valign(Gtk.Align.END)
        
        self.pack_start(self.entry, False, False, 0)
        self.pack_start(self.label, False, False, 0)
    
    def on_entry_changed(self, widget):
        text = re.sub("[^0-9]", "", self.entry.get_text())  # Remove caracteres não numéricos
        formatted_text = self.format_cpf(text)
        self.label.set_markup(f"<span font='8'>{formatted_text}</span>")  # Usa Pango markup para definir o tamanho da fonte

    def format_cpf(self, cpf):
        if len(cpf) > 11:
            cpf = cpf[:11]  # Limita a 11 dígitos
        
        formatted = "".join(cpf)
        if len(cpf) > 9:
            formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        elif len(cpf) > 6:
            formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
        elif len(cpf) > 3:
            formatted = f"{cpf[:3]}.{cpf[3:]}"
        
        return formatted

