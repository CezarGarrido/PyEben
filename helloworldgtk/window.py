from gi import require_versions
require_versions({"Gtk": "3.0", "Poppler": "0.18"})
from gi.repository import Gtk, Poppler
from pathlib import Path
import os
from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa

def convert_html_to_pdf(source_html_path, output_pdf_path):
    """
    Converte um arquivo HTML para PDF usando xhtml2pdf.
    """
    try:
        # Lendo o arquivo HTML
        html_content = Path(source_html_path).read_text(encoding="utf-8")
        
        
        # Criando o arquivo PDF
        with open(output_pdf_path, "wb") as pdf_file:
            # Convertendo o HTML para PDF
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        # Retornando o status da conversão
        return pisa_status.err == 0
    except Exception as e:
        print(f"Erro durante a conversão: {e}")
        return False

def gr():
    # Caminhos do arquivo HTML e do PDF
    source_html = "./reports/recibo2.html"  # Substitua pelo caminho do seu arquivo HTML
    output_pdf = "./reports/recibo2.pdf"  # Caminho para o arquivo PDF de saída

    # Convertendo o HTML para PDF
    if convert_html_to_pdf(source_html, output_pdf):
        print(f"PDF gerado com sucesso: {output_pdf}")
    else:
        print("Falha na conversão do HTML para PDF.")


def generate_report(file_path):
    # Configuração inicial
    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A5),
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
    )

    # Estilos de texto
    styles = getSampleStyleSheet()
    monospaced = ParagraphStyle(
        'Monospaced',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=10,
        textColor=colors.darkgray,
        alignment=0,
    )
    small = ParagraphStyle(
        'Small',
        parent=monospaced,
        fontSize=6,
        alignment=1,
    )
    large = ParagraphStyle(
        'Large',
        parent=monospaced,
        fontSize=12,
        alignment=1,
    )
    default = ParagraphStyle(
        'Default',
        parent=monospaced,
        alignment=0,
    )

    # Componentes do relatório
    elements = []

    # Cabeçalho
    elements.append(Paragraph("LAR EBENEZER = HILDA MARIA CORREA - ADAS", large))
    elements.append(Spacer(1, 10))
    elements.append(
        Table(
            [
                [
                    Paragraph("Utilidade Publica Municipal Lei N.º 1527 de 09/11/88", small),
                    Paragraph("Utilidade Publica Estadual Lei N.º 1493 de 13/05/94", small),
                ]
            ],
            colWidths=[250, 250],
        )
    )
    elements.append(
        Table(
            [
                [
                    Paragraph("Utilidade Publica Federal Portaria N.º 735 de 13/08/01 DOU 14/08/01", small),
                    Paragraph("CEBAS: CCEAS 0030 Resolução N.º 05 de 02/02/04 DOU 05/02/04", small),
                ]
            ],
            colWidths=[250, 250],
        )
    )
    elements.append(Paragraph("Atest. de Reg. no Cons. Nasc. de Assist. Soc. R N.º 0018 Res n.º 05 de 02/02/04", small))
    elements.append(Paragraph("RUA 20 DE DEZEMBRO, N.º 3170, JARDIM RASSLEN, CEP 79.813-280", small))
    elements.append(Paragraph("DOURADOS - MS", large))
    elements.append(Spacer(1, 10))

    # Título principal
    #elements.append(Paragraph("RECIBO DE DOAÇÕES", large))

        # Dados para o título e as linhas
    data = [
        [Paragraph("RECIBO DE DOAÇÕES", large)],  # Título
        [""],  # Espaço vazio
    ]

    # Criando a tabela
    title_table = Table(data, colWidths=[500])  # Largura total da tabela

    # Aplicando linhas horizontais
    title_table.setStyle(
        TableStyle(
            [
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centraliza o conteúdo
                ('LINEBELOW', (0, 0), (-1, 0), 1, 'gray'),  # Linha abaixo do título
                ('LINEABOVE', (0, -1), (-1, -1), 1, 'gray'),  # Linha acima do último espaçamento
                ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à esquerda
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à direita
                ('TOPPADDING', (0, 0), (-1, -1), 5),  # Ajusta espaçamento superior
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # Ajusta espaçamento inferior
            ]
        )
    )

    # Adicionando a tabela ao layout
    elements.append(title_table)

    # Estilo padrão para os parágrafos
    default_style = default  # Substitua com o estilo que você está usando

    # Dados da tabela
    table_data1 = [
        # Linha 1: Recibo e Emitido
        [
            Paragraph("Recibo N.º .....: {{NUMERO_RECIBO}}", default_style),
            Paragraph("Emitido ....: {{DATA_EMISSAO}}", default_style),
        ],
    ]

    table_data2 =[
        # Linha 2: Recebemos de
        [
            Paragraph("Recebemos de ...:", default_style),
            Paragraph(" {{NOME_DOADOR}} ({{CODIGO_DOADOR}})", default_style),

        ],
        # Linha 3: Endereço
        [
            Paragraph("Endereço .......:", default_style),
            Paragraph(" {{END_RUA_DOADOR}} Nº {{END_NUMERO_DOADOR}}", default_style),
            
        ],
        # Linha 4: Bairro
        [
            Paragraph("Bairro .........:", default_style),
            Paragraph("{{END_BAIRRO_DOADOR}}", default_style),

        ],
        # Linha 5: Contato
        [
            Paragraph("Contato ........:", default_style),
            Paragraph("{{CONTATO_DOADOR}}", default_style),

        ],
        # Linha 6: Cidade
        [
            Paragraph("Cidade .........:", default_style),
            Paragraph("{{END_CIDADE_DOADOR}} - {{END_ESTADO_DOADOR}}", default_style),

        ],
        # Linha 7: Valor
        [
            Paragraph("Valor ..........:", default_style),
            Paragraph("{{VALOR_DOADO}}", default_style),

        ],
        # Linha 8: Por Extenso
        [
            Paragraph("Por Extenso ....:", default_style),
            Paragraph("{{VALOR_DOADO_EXTENSO}}", default_style),

        ],
        [
            Paragraph("", default_style),
            Paragraph("", default_style),

        ],
        # Linha 9: Referente a
        [
            Paragraph("Referente a ....:", default_style),
            Paragraph("Doação do mês de agosto", default_style),

        ],
    ]

    # Configuração da tabela com larguras fixas para alinhamento
    col_widths = [300, 200]  # Ajuste a largura das colunas conforme necessário
    col_widths2 = [110, 390]  # Ajuste a largura das colunas conforme necessário

    # Criando a tabela
    complete_table1 = Table(table_data1, colWidths=col_widths)
    complete_table2 = Table(table_data2, colWidths=col_widths2)

    # Aplicando estilos
    complete_table1.setStyle(
        TableStyle(
            [
                # Alinhamento horizontal
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Alinha todas as células da primeira coluna à esquerda
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Alinha a célula da primeira linha da segunda coluna à direita
                # Alinhamento vertical
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alinha todas as células verticalmente no topo
                # Fonte e tamanho
                ('FONTNAME', (0, 0), (-1, -1), 'Courier'),  # Usa fonte monoespaçada
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Define tamanho da fonte
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Define cor do texto
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à esquerda
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à direita
                ('TOPPADDING', (0, 0), (-1, -1), 2),  # Ajusta padding superior
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Ajusta padding inferior
                # Bordas (opcional)
                #('GRID', (0, 0), (-1, -1), 0.25, colors.grey),  # Adiciona grade para depuração (remova para produção)
            ]
        )
    )
 # Aplicando estilos
    complete_table2.setStyle(
        TableStyle(
            [
                # Alinhamento horizontal
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Alinha todas as células da primeira coluna à esquerda
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Alinha a célula da primeira linha da segunda coluna à direita
                # Alinhamento vertical
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alinha todas as células verticalmente no topo
                # Fonte e tamanho
                ('FONTNAME', (0, 0), (-1, -1), 'Courier'),  # Usa fonte monoespaçada
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Define tamanho da fonte
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Define cor do texto
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à esquerda
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à direita
                ('TOPPADDING', (0, 0), (-1, -1), 2),  # Ajusta padding superior
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Ajusta padding inferior
                # Bordas (opcional)
                #('GRID', (0, 0), (-1, -1), 0.25, colors.grey),  # Adiciona grade para depuração (remova para produção)
            ]
        )
    )
    # Adicionando a tabela ao layout
    elements.append(complete_table1)
    elements.append(Spacer(1, 10))
    elements.append(complete_table2)

    elements.append(Spacer(1, 50))


    # Dados para a assinatura
    # Tabela para a linha da assinatura
    line_data = [["", Paragraph("_______________________________", default), ""]]
    line_table = Table(
        line_data,
        colWidths=[150, 200, 150]  # Larguras ajustadas para centralizar a linha
    )

    # Estilo da tabela da linha
    line_table.setStyle(
        TableStyle(
            [
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Centraliza horizontalmente na coluna do meio
                ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),  # Centraliza verticalmente na coluna do meio
                ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à esquerda
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à direita
                ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove padding superior
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove padding inferior
            ]
        )
    )

    # Tabela para o texto "Assinatura"
    signature_data = [["", Paragraph("Assinatura", default_style), ""]]
    signature_table = Table(
        signature_data,
        colWidths=[210, 140, 150]  # Mesma configuração de largura que a tabela da linha
    )

    # Estilo da tabela de "Assinatura"
    signature_table.setStyle(
        TableStyle(
            [
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Centraliza horizontalmente na coluna do meio
                ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),  # Centraliza verticalmente na coluna do meio
                ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à esquerda
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Remove padding à direita
                ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove padding superior
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove padding inferior
            ]
        )
    )

    # Adicionando as tabelas ao layout
    elements.append(line_table)
    elements.append(Spacer(1, 5))  # Espaçamento entre a linha e o texto "Assinatura"
    elements.append(signature_table)
    # Geração do relatório
    doc.build(elements)


# Gera o PDF
generate_report("recibo_doacoes.pdf")

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

        # Botão para imprimir PDF
        self.print_button = Gtk.Button(label="Imprimir PDF")
        self.print_button.connect("clicked", self.on_print_button_clicked)
        vbox.pack_start(self.print_button, False, False, 0)


        # Área de visualização do PDF
        self.pdf_area = Gtk.DrawingArea()
        vbox.pack_start(self.pdf_area, True, True, 0)

        self.document = None
        self.current_page = 0

    def on_print_button_clicked(self, widget):
        lista = {'Rafaela': '19', 'Jose': '15', 'Maria': '22','Eduardo':'24'}
        gr()
        #generate_report("reports.pdf")

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
