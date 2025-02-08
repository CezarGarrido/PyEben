from ...models.user import User
from ...services.user_service import UserService
from ...services.role_service import RoleService
import gi
import re
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from datetime import datetime

class EditForm(Gtk.Window):
    def __init__(self, app, main_window, user_id):
        """Inicializa a janela modal para editar um usuário existente."""
        super().__init__(title="Editar Usuário")
        self.set_default_size(450, 350)
        self.set_transient_for(main_window)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.user_service = UserService()
        self.user_id = user_id
        self.app = app

        # Layout principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=15)
        self.add(vbox)

        # Criando o formulário
        grid = Gtk.Grid(column_spacing=12, row_spacing=12, margin=10)
        vbox.pack_start(grid, True, True, 0)

        # Login (Username)
        grid.attach(Gtk.Label(label="Login:"), 0, 0, 1, 1)
        self.username_entry = Gtk.Entry()
        self.username_entry.set_size_request(250, 30)
        grid.attach(self.username_entry, 1, 0, 2, 1)

        # Email
        grid.attach(Gtk.Label(label="Email:"), 0, 1, 1, 1)
        self.email_entry = Gtk.Entry()
        self.email_entry.connect("changed", self.on_email_changed)
        self.email_entry.set_size_request(250, 30)
        grid.attach(self.email_entry, 1, 1, 2, 1)

        # Senha (opcional na edição)
        grid.attach(Gtk.Label(label="Senha (deixe em branco para manter):"), 0, 2, 1, 1)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_size_request(250, 30)
        grid.attach(self.password_entry, 1, 2, 2, 1)

        # Status (Ativo/Inativo)
        grid.attach(Gtk.Label(label="Status:"), 0, 3, 1, 1)
        self.status_combo = Gtk.ComboBoxText()
        self.status_combo.append("1", "Ativo")
        self.status_combo.append("0", "Inativo")
        self.status_combo.set_size_request(250, 30)
        grid.attach(self.status_combo, 1, 3, 2, 1)

        # Papel (Roles dinâmicos)
        grid.attach(Gtk.Label(label="Nível de acesso:"), 0, 4, 1, 1)
        self.role_combo = Gtk.ComboBoxText()
        self.role_combo.set_size_request(250, 30)
        self.load_roles()
        grid.attach(self.role_combo, 1, 4, 2, 1)

        # Botões
        button_box = Gtk.Box(spacing=15)
        vbox.pack_start(button_box, False, False, 0)

        save_button = Gtk.Button(label="Salvar")
        save_button.set_size_request(100, 35)
        save_button.connect("clicked", self.on_save_clicked)
        button_box.pack_start(save_button, True, True, 0)

        cancel_button = Gtk.Button(label="Cancelar")
        cancel_button.set_size_request(100, 35)
        cancel_button.connect("clicked", self.on_cancel_clicked)
        button_box.pack_start(cancel_button, True, True, 0)

        self.load_user_data()  # Carrega os dados do usuário

    def load_roles(self):
        """Obtém os roles do banco e preenche o ComboBox com ID oculto."""
        service = RoleService()
        roles = service.list_roles()

        if roles:
            for role in roles:
                self.role_combo.append(str(role.id), role.role)  # ID oculto, texto visível
        else:
            self.role_combo.append("0", "default")  # Se nãd houver roles, usa "default"

        self.role_combo.set_active(0)
    def load_user_data(self):
        """Carrega os dados do usuário no formulário."""
        user = self.user_service.get_user_by_id(self.app.logged_user, self.user_id)

        if user:
            self.username_entry.set_text(user.username)
            self.email_entry.set_text(user.email)
            self.status_combo.set_active_id("1" if user.active else "0")
            self.role_combo.set_active_id(str(user.role))
        else:
            self.show_error("Usuário não encontrado!")
            self.destroy()

    def on_save_clicked(self, button):
        """Salva as alterações no usuário."""
        username = self.username_entry.get_text().strip()
        email = self.email_entry.get_text().strip()
        password = self.password_entry.get_text().strip()
        status = bool(int(self.status_combo.get_active_id()))
        role_id = int(self.role_combo.get_active_id())

        if not username or not email:
            self.show_error("Usuário e email são obrigatórios!")
            return

        try:
            user = self.user_service.get_user_by_id(self.user_id)
            if not user:
                self.show_error("Usuário não encontrado!")
                return

            user.username = username
            user.email = email
            user.active = status
            user.role = role_id
            user.updated_at = datetime.now()

            if password:
                user.password = User.hash_password(password)  # Atualiza a senha apenas se fornecida

            if self.user_service.update_user(user):
                self.show_info("Usuário atualizado com sucesso!")
                self.destroy()
            else:
                self.show_error("Erro ao atualizar usuário!")

        except Exception as e:
            self.show_error(f"Erro ao atualizar usuário: {e}")

    def on_cancel_clicked(self, button):
        """Fecha a janela sem salvar."""
        self.destroy()

    def show_error(self, message):
        """Exibe um diálogo de erro."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Erro",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_info(self, message):
        """Exibe um diálogo de sucesso."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Sucesso",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def on_email_changed(self, widget):
        """Valida o email enquanto o usuário digita."""
        email = widget.get_text()
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if not re.match(email_regex, email):
            widget.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("red"))
        else:
            widget.modify_fg(Gtk.StateFlags.NORMAL, None)
