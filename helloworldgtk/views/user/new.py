from ...models.user import User
from ...services.user_service import UserService
from ...services.role_service import RoleService
import gi
import re
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject
from datetime import datetime

class NewForm(Gtk.Window):
    __gsignals__ = {
        "user_added": (GObject.SignalFlags.RUN_FIRST, None, (int,)),  # Agora aceita um argumento tipo str
    }

    def __init__(self, app, main_window):
        """Inicializa a janela modal para adicionar um novo usuário."""
        super().__init__(title="Novo Usuário")
        self.set_default_size(450, 350)
        self.set_transient_for(main_window)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
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

        # Senha
        grid.attach(Gtk.Label(label="Senha:"), 0, 2, 1, 1)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_size_request(250, 30)
        grid.attach(self.password_entry, 1, 2, 2, 1)

        # Status (Ativo/Inativo)
        grid.attach(Gtk.Label(label="Status:"), 0, 3, 1, 1)
        self.status_combo = Gtk.ComboBoxText()
        self.status_combo.append("1", "Ativo")
        self.status_combo.append("0", "Inativo")
        self.status_combo.set_active(0)
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

        self.show_all()

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

    def on_save_clicked(self, button):
        """Salva o novo usuário no banco de dados."""
        username = self.username_entry.get_text().strip()
        email = self.email_entry.get_text().strip()
        password = self.password_entry.get_text().strip()
        status = bool(int(self.status_combo.get_active_id()))  # Converte "1" ou "0" para bool
        role_id = int(self.role_combo.get_active_id())  # Obtém o ID correto da role

        if not username or not email or not password:
            self.show_error("Todos os campos são obrigatórios!")
            return

        try:
            new_user = User(
                company_id=1,
                username=username,
                email=email,
                password=password,
                active=status,
                photo=None,
                role_id=role_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            service = UserService()
            new_user_id = service.create_user(self.app.logged_user, new_user)
            print(f"Usuário criado com ID: {new_user_id}")
            self.emit("user_added", new_user_id)  

            self.destroy()

        except ValueError as e:
            self.show_error(f"Erro ao salvar usuário: {e}")
        except Exception as e:
            self.show_error(f"Erro ao salvar usuário: {e}")

    def on_cancel_clicked(self, button):
        """Fecha a janela sem salvar."""
        self.destroy()

    def show_error(self, message):
        """Exibe um diálogo de erro."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Erro",
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
