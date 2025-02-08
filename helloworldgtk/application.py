from gi import require_versions
require_versions({"Gtk": "3.0"})
from gi.repository import Gtk
from .window import Window
from .login import LoginWindow  # Importa a classe LoginWindow do arquivo login.py

class Application(Gtk.Application):

    def __init__(self):
        super().__init__()
        self.main_window = None
        self.login_window = None
        self.logged_user = None  # Variável para armazenar o usuário logado

    def on_login_success(self, login_window, user):
        print("Login bem-sucedido! Abrindo a janela principal...")
        self.logged_user = user  # Salva o usuário logado na aplicação
        self.login_window.destroy()  # Fecha a janela de login
        self.main_window = Window(self)  # Abre a janela principal
        self.main_window.connect("destroy", lambda _: self.quit())  

        self.add_window(self.main_window)  # Associa à aplicação
        self.main_window.show_all()
        self.main_window.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if not self.login_window:
            self.login_window = LoginWindow()
            self.add_window(self.login_window)  # Adiciona a janela de login à Application
            self.login_window.connect("login_success", self.on_login_success)

        self.login_window.show_all()
        self.login_window.present()
