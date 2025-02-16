import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from .services.user_service import UserService


class LoginWindow(Gtk.Window):
    __gsignals__ = {
        "login_success": (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }

    def __init__(self):
        super().__init__(title="Login")
        self.user_service = UserService()

        self.set_default_size(400, 450)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        # Aplicar estilo CSS
        self.apply_css()

        # Criar uma caixa principal para centralizar o painel
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        self.add(main_box)

        # Painel de login
        login_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=20)
        login_box.set_name("login-box")
        main_box.pack_start(login_box, False, False, 0)

        # Título "Welcome Back"
        title = Gtk.Label(label="Acessar")
        title.set_name("login-title")
        login_box.pack_start(title, False, False, 5)

        # Subtítulo
        #subtitle = Gtk.Label(label="Sign in to access your dashboard, setting and projects.")
        #subtitle.set_name("subtitle")
        #login_box.pack_start(subtitle, False, False, 5)

        # Linha divisória
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        login_box.pack_start(separator, False, False, 5)

        # Campo de e-mail
        email_label = Gtk.Label(label="Login")
        email_label.set_halign(Gtk.Align.START)
        email_label.set_name("label")
        login_box.pack_start(email_label, False, False, 0)

        self.email_entry = Gtk.Entry()
        self.email_entry.set_placeholder_text("Informe o login")
        self.email_entry.set_name("input")
        login_box.pack_start(self.email_entry, False, False, 0)

        # Campo de senha + botão para exibir senha
        pass_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        pass_label = Gtk.Label(label="Senha")
        pass_label.set_halign(Gtk.Align.START)
        pass_label.set_name("label")
        pass_label_box.pack_start(pass_label, True, True, 0)


        login_box.pack_start(pass_label_box, False, False, 0)

        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Informe a senha")
        self.password_entry.set_visibility(False)
        self.password_entry.set_name("input")
        self.password_entry.set_hexpand(True)
        self.password_entry.connect("activate", self.on_login_button_clicked)

        password_box.pack_start(self.password_entry, True, True, 0)
        # Botão para exibir/ocultar senha
        self.show_password_button = Gtk.Button(label="👁")
        self.show_password_button.set_name("toggle-btn")
        self.show_password_button.set_focus_on_click(False)
        self.show_password_button.connect("clicked", self.toggle_password_visibility)
        password_box.pack_start(self.show_password_button, False, False, 0)

        login_box.pack_start(password_box, False, False, 0)

        # Opção "Lembrar por 30 dias"
        remember_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.remember_me = Gtk.CheckButton()
        remember_label = Gtk.Label(label="Manter conectado?")
        remember_label.set_name("label")
        remember_box.pack_start(self.remember_me, False, False, 0)
        remember_box.pack_start(remember_label, False, False, 5)

        login_box.pack_start(remember_box, False, False, 0)

        # Botão de login
        login_button = Gtk.Button(label="Entrar  →")
        login_button.set_name("login-button")
        login_button.connect("clicked", self.on_login_button_clicked)
        login_box.pack_start(login_button, False, False, 10)



    def toggle_password_visibility(self, button):
        self.password_entry.set_visibility(not self.password_entry.get_visibility())

    def on_login_button_clicked(self, button):
        email = self.email_entry.get_text()
        password = self.password_entry.get_text()

        try:
            user = self.user_service.login(email, password)
            self.emit("login_success", user)
        except ValueError as e:
            self.show_error_dialog(str(e))
        except Exception as e:
            self.show_error_dialog(f"Ocorreu um erro ao tentar fazer login: {str(e)}")

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Erro de Login",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def apply_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            #login-box {
                padding: 20px;
                min-width: 300px;
            }

            #login-title {
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }

            #subtitle {
                font-size: 12px;
                color: #777;
            }

            #label {
                font-size: 12px;
                color: #555;
            }

            #input {
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
                border: 1px solid #ccc;
                background-color: white;
                color: black;
            }

            #forgot-password {
                font-size: 12px;
                color: #007BFF;
                text-decoration: underline;
            }

            #toggle-btn {
                background: none;
                border: none;
                color: #999;
                font-size: 14px;
                padding: 2px;
                margin-left: 5px;
            }

            #login-button {
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }

   
            #register-label {
                font-size: 12px;
                color: #555;
            }

            """
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
