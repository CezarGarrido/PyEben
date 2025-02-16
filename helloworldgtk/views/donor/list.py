import gi

from helloworldgtk.widget.datatable import DataTable
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from ...services.donor_service import DonorService  # Certifique-se de que o caminho está correto
from ..tab import BaseTab
from .new import NewForm
from .edit import EditForm

class DonorListForm(BaseTab):
    def __init__(self, app):
        """Inicializa a aba de listagem de doadores."""
        self.app = app
        super().__init__()

    def create_content(self):
        """Cria a tabela de doadores usando o DataTable."""
        self.data_table =  DataTable(
            columns=[
                ("ID", int),
                ("Nome", str),
                ("Status", bool),
                ("CPF/CNPJ", str),
                ("Criado em", str),
                ("Atualizado em", str),
            ],
            fetch_data_function=self.fetch_donors,
            column_formatters={"Status": self.format_status},  # Personalizando a coluna Status
            rows_per_page_options=[10, 25, 50, 100]
        )
        
        return self.data_table

    def fetch_donors(self, search_term, offset, limit):
        """Busca doadores no banco de dados usando paginação."""
        service = DonorService()
        total_records = service.count(self.app.logged_user, search_term)
        donors = service.search(self.app.logged_user, search_term, offset, limit)

        # Retorna os doadores formatados e o número total de registros
        return [(d.id, d.name, d.active, d.cpf if d.person_type != "PJ" else d.cnpj,
                 d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else "N/A",
                 d.updated_at.strftime("%Y-%m-%d %H:%M:%S") if d.updated_at else "N/A") for d in donors], total_records
    
    def on_rows_per_page_changed(self, combo):
        """Atualiza a quantidade de registros por página ao alterar o dropdown."""
        self.items_per_page = int(combo.get_active_text())  # Obtém o novo valor selecionado
        self.current_page = 0  # Reinicia para a primeira página ao mudar a quantidade de registros
        self.load_donors()  # Recarrega a tabela com a nova quantidade
        
    def format_status(self, column, cell, model, iter, data):
        """Formata a coluna Status para exibir "Ativo" em verde e "Inativo" em vermelho."""
        active = model[iter][2]  # Índice da coluna "Status"
        cell.set_property("text", "Ativo" if active else "Inativo")
        cell.set_property("foreground", "green" if active else "red")
    
    def get_toolbar_actions(self):
        """Define os botões e separadores da toolbar."""
        return [
            ("new", "document-new", "Novo", self.on_new_clicked),
            ("edit", "document-edit", "Editar", self.on_edit_user_clicked),
            ("delete", "edit-delete", "Desativar", self.on_edit_user_clicked),
            None,  # Separador
            ("close", "window-close", "Fechar", self.on_close_clicked),
        ]

    def add_column(self, title, column_id):
        """Adiciona uma coluna ordenável à TreeView."""
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=column_id)
        column.set_sort_column_id(column_id)
        column.set_clickable(True)
        self.treeview.append_column(column)

    def add_status_column(self, title, column_id):
        """Adiciona uma coluna de status com cor para ativo/inativo."""
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=column_id)
        
        def set_status_color(column, cell, model, iter, data):
            active = model[iter][column_id]
            cell.set_property("text", "Ativo" if active else "Inativo")
            cell.set_property("foreground", "green" if active else "red")

        column.set_cell_data_func(renderer, set_status_color, None)
        self.treeview.append_column(column)

    def load_donors(self):
        """Obtém os doadores da página atual e atualiza a paginação corretamente."""
        service = DonorService()

        # Contar total de registros no banco
        total_records = service.count(self.app.logged_user)  # Contagem do banco
        self.total_pages = max(1, (total_records // self.items_per_page) + (1 if total_records % self.items_per_page else 0))

        # Calcular OFFSET
        offset = self.current_page * self.items_per_page

        # Buscar doadores da página atual
        self.all_data = service.search(self.app.logged_user, search_term="", offset=offset, limit=self.items_per_page)

        self.update_table()
        self.update_pagination_buttons()


    def update_table(self):
        """Atualiza a visualização da tabela com os dados carregados."""
        self.store.clear()

        for user in self.all_data:
            self.store.append((
                user.id,
                user.name,
                user.active,
                user.cpf if user.person_type != "PJ" else user.cnpj,
                user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "N/A",
                user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else "N/A",
            ))

    def update_pagination_buttons(self):
        """Atualiza os botões de paginação corretamente, sem botões numéricos."""

        # O total de páginas deve ser baseado no número total de registros no banco
        total_pages = self.total_pages  # Agora usamos o valor correto da contagem do banco

        # Remover botões antigos antes de adicionar novos
        for child in self.pagination_box.get_children():
            self.pagination_box.remove(child)

        # Criar botões de navegação
        self.first_button = Gtk.Button(label="«")
        self.first_button.connect("clicked", self.on_first_page)

        self.prev_button = Gtk.Button(label="‹")
        self.prev_button.connect("clicked", self.on_prev_page)

        self.next_button = Gtk.Button(label="›")
        self.next_button.connect("clicked", self.on_next_page)

        self.last_button = Gtk.Button(label="»")
        self.last_button.connect("clicked", self.on_last_page)

        # Adicionar os botões na ordem correta
        self.pagination_box.pack_start(self.first_button, False, False, 0)
        self.pagination_box.pack_start(self.prev_button, False, False, 0)
        self.pagination_box.pack_start(self.next_button, False, False, 0)
        self.pagination_box.pack_start(self.last_button, False, False, 0)

        # Atualizar estados dos botões (ativar/desativar corretamente)
        self.first_button.set_sensitive(self.current_page > 0)
        self.prev_button.set_sensitive(self.current_page > 0)
        self.next_button.set_sensitive(self.current_page < total_pages - 1)
        self.last_button.set_sensitive(self.current_page < total_pages - 1)

        self.pagination_box.show_all()


    def on_first_page(self, button):
        """Vai para a primeira página e recarrega os doadores."""
        self.current_page = 0
        self.load_donors()

    def on_prev_page(self, button):
        """Vai para a página anterior e recarrega os doadores."""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_donors()

    def on_next_page(self, button):
        """Vai para a próxima página e recarrega os doadores."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_donors()

    def on_last_page(self, button):
        """Vai para a última página e recarrega os doadores."""
        self.current_page = self.total_pages - 1
        self.load_donors()


    def on_page_selected(self, button, page_index): self.current_page = page_index; self.update_table()

    def on_search(self, entry):
        """Filtra os doadores pelo nome ou ID e atualiza a paginação corretamente."""
        search_text = entry.get_text().strip().lower()
        service = DonorService()

        # Contar registros filtrados no banco
        total_records = service.count(self.app.logged_user, search_term=search_text)
        self.total_pages = max(1, (total_records // self.items_per_page) + (1 if total_records % self.items_per_page else 0))

        # Calcular OFFSET
        offset = self.current_page * self.items_per_page

        # Buscar doadores da página atual com filtro
        self.all_data = service.search(self.app.logged_user, search_term=search_text, offset=offset, limit=self.items_per_page)

        self.update_table()
        self.update_pagination_buttons()


    def on_close_clicked(self, action): self.destroy()
    def on_new_clicked(self, action): NewForm(self.app, self.get_toplevel()).show_all()
    def on_edit_user_clicked(self, button): EditForm(self.app, self.get_toplevel(), self.get_selected_user_id()).show_all()
    def on_deactivate_user_clicked(self, button):
        """Desativa o usuário selecionado após confirmação."""
        user_id = self.get_selected_user_id()
        
        if not user_id:
            self.show_error_dialog("Nenhum usuário selecionado para desativar.")
            return

        # Criar um popup de confirmação
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Confirmação",
        )
        dialog.format_secondary_text(f"Tem certeza de que deseja desativar o usuário com ID {user_id}?")
        
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            try:
                service = DonorService()
                success = service.deactivate(self.app.logged_user, user_id)

                if success:
                    self.show_info_dialog("Usuário desativado com sucesso!")
                    self.data_table.load_data()  # Atualiza a tabela
                else:
                    self.show_error_dialog("Erro ao desativar o usuário.")

            except Exception as e:
                self.show_error_dialog(f"Erro ao desativar usuário: {str(e)}")

    def get_selected_user_id(self):
        """Obtém o ID do usuário selecionado."""
        selected_row = self.data_table.get_selected_row()
        return selected_row[0] if selected_row else None  # Assume que o ID está na primeira coluna
