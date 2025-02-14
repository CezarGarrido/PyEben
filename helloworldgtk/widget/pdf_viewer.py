from gi import require_versions
require_versions({"Gtk": "3.0", "Poppler": "0.18"})
from gi.repository import Gtk, Poppler, Gdk, GLib
import cairo
from pathlib import Path

class PDFViewer(Gtk.Window):

    def __init__(self, app, parent, pdf_file_path):
        super().__init__(title="Visualizador de PDF")
        self.set_default_size(770, 500)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.app = app
        self.pdf_file_path = pdf_file_path  # Salvar caminho do PDF para impressão

        # Layout principal com barra de navegação
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Barra de ferramentas
        toolbar = Gtk.Toolbar()
        vbox.pack_start(toolbar, False, False, 0)

        # Botão Anterior
        prev_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_BACK)
        prev_button.connect("clicked", self.on_previous_page)
        toolbar.insert(prev_button, 0)

        # Botão Próxima
        next_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_FORWARD)
        next_button.connect("clicked", self.on_next_page)
        toolbar.insert(next_button, 1)

        # Separador
        toolbar.insert(Gtk.SeparatorToolItem(), 2)

        # Label da página
        self.page_label = Gtk.Label(label="Página 1")
        page_item = Gtk.ToolItem()
        page_item.add(self.page_label)
        toolbar.insert(page_item, 3)

        # Separador
        toolbar.insert(Gtk.SeparatorToolItem(), 4)

        # Botão de Zoom In
        zoom_in_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ZOOM_IN)
        zoom_in_button.connect("clicked", self.on_zoom_in)
        toolbar.insert(zoom_in_button, 5)

        # Botão de Zoom Out
        zoom_out_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ZOOM_OUT)
        zoom_out_button.connect("clicked", self.on_zoom_out)
        toolbar.insert(zoom_out_button, 6)

        # Separador
        toolbar.insert(Gtk.SeparatorToolItem(), 7)

        # Botão de Imprimir
        print_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_PRINT)
        print_button.connect("clicked", self.on_print_pdf)
        toolbar.insert(print_button, 8)

        # Área de rolagem para o PDF
        self.scrolled_window = Gtk.ScrolledWindow()
        vbox.pack_start(self.scrolled_window, True, True, 0)

        # Área de desenho para exibir o PDF
        self.pdf_area = Gtk.DrawingArea()
        self.pdf_area.connect("draw", self.on_draw_pdf)
        self.scrolled_window.add(self.pdf_area)

        self.document = None
        self.current_page = 0
        self.zoom_level = 1.0  # Fator de zoom

        # Carregar o PDF antes de exibir a janela
        self.load_pdf(pdf_file_path)

        # Eventos de rolagem para zoom
        self.pdf_area.add_events(Gdk.EventMask.SCROLL_MASK)
        self.pdf_area.connect("scroll-event", self.on_zoom)

        # Exibir a janela
        self.show_all()

    def load_pdf(self, file_path):
        try:
            file_uri = self.convert_path_to_uri(file_path)
            self.document = Poppler.Document.new_from_file(file_uri, None)

            if not self.document or self.document.get_n_pages() == 0:
                raise ValueError("O documento não pôde ser carregado ou está vazio.")

            print(f"PDF carregado com {self.document.get_n_pages()} páginas.")
            self.current_page = 0
            self.update_page_label()
            self.render_page()

        except Exception as e:
            print(f"Erro ao abrir o PDF: {e}")

    def render_page(self):
        try:
            if self.document:
                page = self.document.get_page(self.current_page)
                if not page:
                    raise ValueError("Não foi possível carregar a página do PDF.")

                width, height = page.get_size()
                width *= self.zoom_level
                height *= self.zoom_level

                print(f"Redimensionando para {width}x{height} (Zoom: {self.zoom_level:.1f})")

                # Configurar a área de desenho
                self.pdf_area.set_size_request(int(width), int(height))
                self.pdf_area.queue_draw()
        except Exception as e:
            print(f"Erro ao renderizar o PDF: {e}")

    def on_draw_pdf(self, widget, cr):
        try:
            if self.document:
                page = self.document.get_page(self.current_page)
                if page:
                    width, height = page.get_size()
                    width *= self.zoom_level
                    height *= self.zoom_level

                    # Obtém o tamanho da área de desenho do Gtk.DrawingArea
                    allocation = widget.get_allocation()
                    area_width = allocation.width
                    area_height = allocation.height

                    # Calcula a posição centralizada
                    x_offset = (area_width - width) / 2 if area_width > width else 0
                    y_offset = (area_height - height) / 2 if area_height > height else 0

                    # print(f"Centralizando em X: {x_offset}, Y: {y_offset}")

                    # Criando uma superfície temporária para renderizar a página
                    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
                    ctx = cairo.Context(surface)

                    # Define fundo branco
                    ctx.set_source_rgb(1, 1, 1)
                    ctx.paint()

                    # Aplica zoom na página
                    ctx.scale(self.zoom_level, self.zoom_level)
                    page.render(ctx)

                    # Move a renderização para a posição centralizada
                    cr.translate(x_offset, y_offset)

                    # Renderiza na área de desenho
                    cr.set_source_surface(surface, 0, 0)
                    cr.paint()
        except Exception as e:
            print(f"Erro ao desenhar PDF: {e}")

    def on_next_page(self, widget):
        if self.document and self.current_page < self.document.get_n_pages() - 1:
            self.current_page += 1
            self.update_page_label()
            self.render_page()

    def on_previous_page(self, widget):
        if self.document and self.current_page > 0:
            self.current_page -= 1
            self.update_page_label()
            self.render_page()

    def on_zoom_in(self, widget):
        self.zoom_level *= 1.1
        self.render_page()

    def on_zoom_out(self, widget):
        self.zoom_level /= 1.1
        self.render_page()

    def on_zoom(self, widget, event):
        """ Zoom in/out com rolagem do mouse """
        if event.direction == Gdk.ScrollDirection.UP:
            self.zoom_level *= 1.1
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.zoom_level /= 1.1
        self.render_page()

    def update_page_label(self):
        """ Atualiza a exibição do número da página """
        total_pages = self.document.get_n_pages()
        self.page_label.set_text(f"Página {self.current_page + 1} de {total_pages}")

    def convert_path_to_uri(self, file_path):
        return Path(file_path).absolute().as_uri()
    
    def on_print_pdf(self, widget):
        """ Função para imprimir o PDF em formato A5 Landscape """
        print("Imprimindo PDF em A5 Landscape...")

        print_op = Gtk.PrintOperation()
        print_op.set_n_pages(self.document.get_n_pages())
        print_op.set_unit(Gtk.Unit.MM)
        print_op.set_export_filename("recibo.pdf")
        print_op.set_embed_page_setup(True)
        print_op.set_allow_async(True)
        # Configurar tamanho da página A5 e orientação Landscape
        page_setup = Gtk.PageSetup()

        # Definir tamanho manualmente em milímetros (A5 = 148mm x 210mm)
        a5_width_mm = 210
        a5_height_mm = 148
        paper_size = Gtk.PaperSize.new_custom("A5_Landscape", "A5 Landscape", a5_height_mm, a5_width_mm, Gtk.Unit.MM)

        # Configurar a orientação para Landscape
        page_setup.set_orientation(Gtk.PageOrientation.LANDSCAPE)
        page_setup.set_paper_size(paper_size)

        # Aplicar configurações ao PrintOperation
        print_op.set_default_page_setup(page_setup)


        print_op.set_use_full_page(True)

        settings = Gtk.PrintSettings()

        dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if dir is None:
            dir = GLib.get_home_dir()
        ext = '.pdf'

        uri = "file://%s/recibo%s" % (dir, ext)
        
        settings.set(Gtk.PRINT_SETTINGS_OUTPUT_URI, uri)
        
        print_op.set_print_settings(settings)
        
        def draw_page(print_op, context, page_nr):
            """ Renderiza cada página para impressão """
            cr = context.get_cairo_context()
            page = self.document.get_page(page_nr)

            # Tamanho real da página do documento
            width, height = page.get_size()

            # Como o A5 Landscape tem a largura maior que a altura, invertemos
            a5_landscape_width = context.get_width()
            a5_landscape_height = context.get_height()

            # Escalar para caber no A5 landscape
            scale_x = a5_landscape_width / width
            scale_y = a5_landscape_height / height
            scale = min(scale_x, scale_y)

            # Transladar para centralizar no papel
            x_offset = (a5_landscape_width - (width * scale)) / 2
            y_offset = (a5_landscape_height - (height * scale)) / 2

            # Aplicar escala e posição
            cr.translate(x_offset, y_offset)
            cr.scale(scale, scale)
            page.render(cr)

        print_op.connect("draw-page", draw_page)

        res = print_op.run(Gtk.PrintOperationAction.PRINT_DIALOG, self)

        if res == Gtk.PrintOperationResult.ERROR:
            print("Erro ao imprimir o documento.")
        elif res == Gtk.PrintOperationResult.APPLY:
            print("Documento enviado para impressão com sucesso!")