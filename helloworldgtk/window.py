from gi import require_versions
require_versions({"Gtk": "3.0", "Poppler": "0.18"})
from gi.repository import Gtk, Poppler
from pathlib import Path

class Window(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Visualizador de PDF")
        self.set_default_size(800, 600)

        # Layout principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Botão para selecionar arquivo PDF
        self.button = Gtk.Button(label="Selecionar PDF")
        self.button.connect("clicked", self.on_button_clicked)
        vbox.pack_start(self.button, False, False, 0)

        # Área de visualização do PDF
        self.pdf_area = Gtk.DrawingArea()
        vbox.pack_start(self.pdf_area, True, True, 0)

        self.document = None
        self.current_page = 0

    def on_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Selecione um arquivo PDF",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Arquivos PDF")
        file_filter.add_mime_type("application/pdf")
        dialog.add_filter(file_filter)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            self.load_pdf(file_path)
        dialog.close()

    def load_pdf(self, file_path):
        try:
            file_uri = self.convert_path_to_uri(file_path)
            print(file_uri)
            self.document = Poppler.Document.new_from_file(file_uri, None)
            if not self.document:
                raise ValueError("O documento não pôde ser carregado.")

            self.current_page = 0
            self.render_page()
        except Exception as e:
            self.show_message(f"Erro ao abrir o PDF: {e}")

    def convert_path_to_uri(self, file_path):
        return Path(file_path).absolute().as_uri()

    def render_page(self):
        try:
            if self.document:
                page = self.document.get_page(self.current_page)
                if not page:
                    raise ValueError("Não foi possível carregar a página do PDF.")

                width, height = page.get_size()

                # Configurando a área de desenho
                self.pdf_area.set_size_request(int(width), int(height))
                self.pdf_area.connect("draw", self.on_draw_pdf, page)
                self.pdf_area.queue_draw()
        except Exception as e:
            self.show_message(f"Erro ao renderizar o PDF: {e}")
            
    def on_draw_pdf(self, widget, cr, page):
        page.render(cr)
        return False

    def show_message(self, message):
        msg_dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Informação",
        )
        msg_dialog.format_secondary_text(message)
        msg_dialog.run()
        msg_dialog.destroy()
