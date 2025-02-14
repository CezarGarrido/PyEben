import locale
import gi

from helloworldgtk.widget.pdf_viewer import PDFViewer

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ...services.donation_service import DonationService  # Certifique-se de que o caminho está correto

from ..tab import BaseTab
from .form import NewForm
from .form import EditForm

class DonationListForm(BaseTab):
    def __init__(self, app):
        """
        Inicializa a aba de listagem de doações.
        :param app: Instância da Application, usada para obter o usuário logado.
        """
        self.app = app  # Guarda a instância da aplicação

        super().__init__()

    def create_content(self):
        """Cria o conteúdo da aba, que consiste em uma tabela de doações."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Criando uma área de rolagem para a tabela
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scrolled_window, True, True, 5)

        # Criando um modelo de dados para a tabela (ListStore)
        self.store = Gtk.ListStore(
            int,    # ID
            str,    # Doador
            str,    # Quantia
            str,    # Pago
            str,    # Data de recebimento
            str,    # Hora de recebimento
            str,    # Notas
            str,    # Criado em
            str,    # Atualizado em
        )

        # Chamando a função para buscar as doações reais
        self.load_donations()

        # Criando a TreeView com base no modelo de dados
        self.treeview = Gtk.TreeView(model=self.store)
        scrolled_window.add(self.treeview)

        # Adicionando colunas à tabela
        self.add_column("ID", 0)
        self.add_column("Doador", 1)
        self.add_column("Quantia", 2)
        self.add_column("Pago", 3)
        self.add_column("Dt.Recebimento", 4)
        self.add_column("Hr. Recebimento", 5)
        self.add_column("Obs.", 6)
        self.add_column("Criado em", 7)
        self.add_column("Atualizado em", 8)

        return box
    
    def load_donations(self):
        """Obtém as doações do banco de dados e adiciona à tabela."""
        service = DonationService()
        donations = service.list(self.app.logged_user)
        self.store.clear()

        if donations:
            for donation in donations:
                valor_formatado = locale.currency(donation.amount, grouping=True, symbol=True)
                self.store.append((
                    donation.id,
                    donation.donor.name,
                    valor_formatado,
                    "Sim" if donation.paid else "Não",
                    donation.received_at.strftime("%Y-%m-%d") if donation.paid and donation.received_at else "N/A",
                    donation.received_time if donation.paid and donation.received_time else "N/A",
                    donation.notes if donation.notes else "",
                    donation.created_at.strftime("%Y-%m-%d %H:%M:%S") if donation.created_at else "N/A",
                    donation.updated_at.strftime("%Y-%m-%d %H:%M:%S") if donation.updated_at else "N/A",
                ))
        else:
            print("Nenhuma doação encontrada no banco de dados.")

    def get_toolbar_actions(self):
        """Define os botões e separadores da toolbar."""
        return [
            ("new", "document-new", "Novo", self.on_new_clicked),
            ("edit", "document-edit", "Editar", self.on_edit_user_clicked),
            ("delete", "edit-delete", "Excluir", self.on_delete_user_clicked),
            None,  # Separador
            ("pdf", "document-print", "Gerar Recibo", self.on_generate_receipt),

            None,
            ("close", "window-close", "Fechar", self.on_close_clicked),
        ]

    def add_column(self, title, column_id):
        """Adiciona uma coluna à TreeView."""
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=column_id)
        self.treeview.append_column(column)

    def add_status_column(self, title, column_id):
        """Adiciona uma coluna de status com um badge de cor."""
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=column_id)
        
        # Define a cor do texto para indicar o status
        def set_status_color(column, cell, model, iter, data):
            active = model[iter][column_id]
            cell.set_property("text", "Ativo" if active else "Inativo")
            cell.set_property("foreground", "green" if active else "red")

        column.set_cell_data_func(renderer, set_status_color, None)
        self.treeview.append_column(column)

    def on_save_clicked(self, action): print("Salvar")
    def on_close_clicked(self, action): 
        self.destroy()

    def on_new_clicked(self, action):
        form = NewForm(self.app, self.get_toplevel())
        form.connect("donation_saved", self.on_donation_saved)
        form.show_all()

    def on_donation_saved(self, w, donation_id):
        print(f"Doação salva com ID: {donation_id}")

                
        self.load_donations()
         
    def on_generate_receipt(self, action):
        # Obtém o modelo e a seleção atual do TreeView
        selection = self.treeview.get_selection()
        model, tree_iter = selection.get_selected()

        if tree_iter:
            # Obtém o ID do usuário a partir da seleção
            donation_id = model[tree_iter][0]  # Supondo que o ID esteja na primeira coluna
            service = DonationService()
            # Criar um diálogo perguntando se deseja gerar o recibo
            dialog = Gtk.MessageDialog(
                transient_for=self.get_toplevel(),
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Recibo",
            )
            dialog.format_secondary_text("Deseja gerar um recibo para esta doação?")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                pdf_path = service.generate_receipt(self.app.logged_user, donation_id)
                v = PDFViewer(self.app, self.get_toplevel(), pdf_path)
                
                
    def on_open_clicked(self, action): print("Abrir")
    def on_add_event_clicked(self, action): print("Editar")
    def on_delete_user_clicked(self, button):
        """
        Obtém o usuário selecionado na listagem e o exclui do banco de dados.
        """
        # Obtém o modelo e a seleção atual do TreeView
        selection = self.treeview.get_selection()
        model, tree_iter = selection.get_selected()

        if tree_iter:
            # Obtém o ID do usuário a partir da seleção
            user_id = model[tree_iter][0]  # Supondo que o ID esteja na primeira coluna
            parent_window = self.get_toplevel()
            # Confirmação antes da exclusão
            dialog = Gtk.MessageDialog(
                transient_for=parent_window,
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Confirmação",
            )
            dialog.format_secondary_text(f"Tem certeza de que deseja excluir a Doação com ID {user_id}?")
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                try:
                    # Chama a função de exclusão no UserService
                    service = DonationService()

                    if service.deactivate(self.app.logged_user, user_id):
                        self.show_info_dialog("Doação excluído com sucesso!")
                        self.load_donations()  # Atualiza a listagem
                    else:
                        self.show_error_dialog("Erro ao excluir o doação. ID não encontrado.")

                except Exception as e:
                    self.show_error_dialog(f"Erro ao excluir doação: {str(e)}")
        else:
            self.show_error_dialog("Nenhum doação selecionado.")

    def on_edit_user_clicked(self, button):
        """
        Obtém o doação selecionado e abre o formulário de edição.
        """
        selection = self.treeview.get_selection()
        model, tree_iter = selection.get_selected()

        if tree_iter:
            user_id = model[tree_iter][0]  # Obtém o ID do usuário
            edit_form = EditForm(self.app, self.get_toplevel(), user_id)  # Abre a janela de edição
            edit_form.connect("donation_saved", lambda _, user_id: self.load_donations())
            edit_form.show_all()
        else:
            self.show_error_dialog("Nenhum usuário selecionado.")

    def show_info_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Informação",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Erro!",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()