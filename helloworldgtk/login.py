import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject
from .services.user_service import UserService

class LoginWindow(Gtk.Window):
    # Define um sinal personalizado chamado "login_success"
    __gsignals__ = {
        "login_success": (GObject.SignalFlags.RUN_FIRST, None, (object,)),  # Agora aceita um argumento tipo str
    }

    def __init__(self):
        super().__init__(title="Login")
        self.user_service = UserService()  # Instância do serviço de login
        
        self.set_default_size(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER)  # Centraliza a janela na tela

        # Cria um Grid para organizar os widgets
        grid = Gtk.Grid(margin=10, row_spacing=10, column_spacing=10)
        self.add(grid)

        # Adiciona um Label com o texto "BEM VINDO" formatado como título
        welcome_label = Gtk.Label()
        welcome_label.set_markup("<span size='x-large' weight='bold'>BEM VINDO</span>")  # Título maior e em negrito
        welcome_label.set_halign(Gtk.Align.CENTER)  # Centraliza o texto horizontalmente
        welcome_label.set_margin_bottom(20)  # Adiciona uma margem abaixo do título

        # Cria os widgets
        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("Username")
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Password")
        self.password_entry.set_visibility(False)
        self.password_entry.connect("activate", self.on_login_button_clicked)

        login_button = Gtk.Button(label="Login")
        login_button.connect("clicked", self.on_login_button_clicked)
        login_button.set_margin_top(10)  # Adiciona uma margem abaixo do título

        # Centraliza os widgets no Grid
        grid.set_halign(Gtk.Align.CENTER)  # Centraliza horizontalmente
        grid.set_valign(Gtk.Align.CENTER)  # Centraliza verticalmente

        # Adiciona os widgets ao Grid
        grid.attach(welcome_label, 0, 0, 2, 1)  # Ocupa duas colunas para centralizar o título
        grid.attach(Gtk.Label(label="Username:"), 0, 1, 1, 1)
        grid.attach(self.username_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Password:"), 0, 2, 1, 1)
        grid.attach(self.password_entry, 1, 2, 1, 1)
        grid.attach(login_button, 0, 3, 2, 1)  # Ocupa duas colunas para centralizar o botão

    def on_login_button_clicked(self, button):
        username = self.username_entry.get_text()
        password = self.password_entry.get_text()

        try:
            user = self.user_service.login(username, password)
            self.emit("login_success", user)  

        except ValueError as e:  # Captura erro de login
            self.show_error_dialog(str(e))

        except Exception as e:  # Captura erros inesperados
            self.show_error_dialog(f"Ocorreu um erro ao tentar fazer login: {str(e)}")

    def show_error_dialog(self, message):
        
        print(message)
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Login failed!",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()