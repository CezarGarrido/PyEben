from gi import require_versions

require_versions({"Gtk": "3.0", "Poppler": "0.18"})

from gi.repository import Gtk, GLib
from datetime import datetime
from .views.tab import BaseTab, WelcomeTab
from .views.user.list import UserList
from .views.employee.list import EmployeeListForm
from .views.donor.list import DonorListForm
from .views.agenda.list import AgendaList

class Window(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)
        self.app = app  # Referência para a aplicação principal
        self.set_title("Ebenezer")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Cria uma caixa vertical para a janela
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Cria o menu principal
        menu_bar = Gtk.MenuBar()
        file_menu = Gtk.MenuItem(label="Arquivo")
        menu_bar.append(file_menu)

        edit_menu = Gtk.MenuItem(label="Editar")
        menu_bar.append(edit_menu)

        agenda_menu = Gtk.MenuItem(label="Agenda")
        agenda_menu.connect("activate", self.on_agenda_clicked)

        menu_bar.append(agenda_menu)

        doacao_menu = Gtk.MenuItem(label="Doações")
        menu_bar.append(doacao_menu)

        cadastros_menu = Gtk.MenuItem(label="Cadastros")
        menu_bar.append(cadastros_menu)

        # Submenu de "Cadastros"
        cadastros_submenu = Gtk.Menu()
        cadastros_menu.set_submenu(cadastros_submenu)

        doadores_item = Gtk.MenuItem(label="Doadores")
        doadores_item.connect("activate", self.on_donors_clicked)
        cadastros_submenu.append(doadores_item)


        funcionarios_item = Gtk.MenuItem(label="Funcionários")
        funcionarios_item.connect("activate", self.on_funcionarios_clicked)
        cadastros_submenu.append(funcionarios_item)

        usuarios_item = Gtk.MenuItem(label="Usuários")
        usuarios_item.connect("activate", self.on_usuarios_clicked)
        cadastros_submenu.append(usuarios_item)

        about_menu = Gtk.MenuItem(label="Sobre")
        menu_bar.append(about_menu)
        vbox.pack_start(menu_bar, False, False, 0)

        # Criando a Toolbar fixa
        self.toolbar = Gtk.Toolbar()
        self.toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        vbox.pack_start(self.toolbar, False, False, 0)

        # Criando o Notebook (Sistema de Abas)
        self.notebook = Gtk.Notebook()
        self.notebook.set_show_border(False)  # Remove a borda do Notebook
        vbox.pack_start(self.notebook, True, True, 0)

        # Criando e adicionando abas
        self.pages = {}
        self.add_tab("Bem-vindo", WelcomeTab())

        # Detecta quando a aba é alterada
        self.notebook.connect("switch-page", self.on_tab_changed)

        # Atualiza a toolbar para a aba inicial
        self.on_tab_changed(self.notebook, self.notebook.get_nth_page(0), 0)

        # Criando a Status Bar
        self.statusbar = Gtk.Statusbar()
        self.statusbar_context_id = self.statusbar.get_context_id("status")
        self.statusbar.set_size_request(-1, 20)  # Define a altura desejada (20 pixels)

        vbox.pack_end(self.statusbar, False, False, 0)

        # Atualiza o status bar com o usuário e hora
        self.update_status_bar()
        GLib.timeout_add(1000, self.update_status_bar)  # Atualiza a cada segundo

        self.show_all()

    def add_tab(self, title, tab_page):
        """Adiciona uma aba ao notebook ou foca em uma já existente."""
        if not isinstance(tab_page, BaseTab):
            raise TypeError(f"A aba '{title}' não implementa BaseTab.")
    
        # Verifica se a aba já existe
        for i in range(self.notebook.get_n_pages()):
            existing_page = self.notebook.get_nth_page(i)
            tab_label = self.notebook.get_tab_label(existing_page)
            if tab_label and tab_label.get_children()[0].get_text() == title:
                self.notebook.set_current_page(i)
                return  # Se a aba já existe, apenas foca nela
    
        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.set_focus_on_click(False)
        close_button.add(Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.SMALL_TOOLBAR))
        close_button.connect("clicked", self.on_close_tab_clicked)
    
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        title_box.pack_start(Gtk.Label(label=title), True, True, 0)
        title_box.pack_start(close_button, False, False, 0)
        title_box.show_all()
    
        self.notebook.append_page(tab_page, title_box)
        self.pages[tab_page] = tab_page.get_toolbar_actions()
        self.notebook.set_current_page(self.notebook.get_n_pages() - 1)

    def on_tab_changed(self, notebook, page, page_num):
        """Atualiza a toolbar conforme a aba ativa."""
        for child in self.toolbar.get_children():
            self.toolbar.remove(child)

        toolbar_actions = self.pages.get(page, [])
        for action in toolbar_actions:
            if action is None:
                separator = Gtk.SeparatorToolItem()
                separator.set_draw(True)
                self.toolbar.insert(separator, -1)
            else:
                action_id, icon_name, label, callback = action
                button = self.create_toolbar_button(icon_name, label, callback)
                self.toolbar.insert(button, -1)

        self.toolbar.show_all()

    def create_toolbar_button(self, icon_name, label, callback):
        """Cria um botão de toolbar com um ícone personalizado."""
        button = Gtk.ToolButton()
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        button.set_icon_widget(icon)
        button.set_label(label)
        button.connect("clicked", callback)
        return button
    
    def on_close_tab_clicked(self, button):
        """Fecha a aba correspondente ao botão de fechar."""
        for i in range(self.notebook.get_n_pages()):
            tab_label = self.notebook.get_tab_label(self.notebook.get_nth_page(i))
            if tab_label is not None and button in tab_label.get_children():
                self.notebook.remove_page(i)
                break

    def on_funcionarios_clicked(self, widget):
        print("Submenu Funcionários clicado!")
        self.add_tab("Funcionários", EmployeeListForm(self.app))

    def on_donors_clicked(self, widget):
        print("Submenu Doadores clicado!")
        self.add_tab("Doadores", DonorListForm(self.app))


    def on_usuarios_clicked(self, widget):
        print("Submenu Usuários clicado!")
        self.add_tab("Usuários", UserList(self.app))

    def on_agenda_clicked(self, widget):
        self.add_tab("Agenda", AgendaList(self.app))
    def update_status_bar(self):
        """Atualiza o status bar com o usuário logado e a hora atual."""
        self.statusbar.pop(self.statusbar_context_id)  # Remove mensagens anteriores
        current_time = datetime.now().strftime("%H:%M:%S")

        if self.app.logged_user:
            user_info = f"Usuário: {self.app.logged_user.username} | {current_time}"
        else:
            user_info = f"Usuário não logado | {current_time}"

        self.statusbar.push(self.statusbar_context_id, user_info)
        return True  # Retorna True para manter o timeout ativo
