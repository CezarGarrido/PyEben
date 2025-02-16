from gi import require_versions


require_versions({"Gtk": "3.0", "Poppler": "0.18"})

from gi.repository import Gtk, GLib, Gdk
from datetime import datetime
from .views.tab import BaseTab, WelcomeTab
from .views.user.list import UserList
from .views.employee.list import EmployeeListForm
from .views.donor.list import DonorListForm
from .views.agenda.list import AgendaList
from .views.donation.list import DonationListForm

class Window(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)
        self.app = app  # Referência para a aplicação principal
        self.set_title("Ebenezer")
        self.set_default_size(850, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.font_size = 14
        # Cria uma caixa vertical para a janela
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.menu_bar = self.create_menu_bar()
        
        vbox.pack_start(self.menu_bar, False, False, 0)

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
       
        # Adicionar atalhos de teclado
        self.connect("key-press-event", self.on_key_press)

        # Atualiza o status bar com o usuário e hora
        self.update_status_bar()
        GLib.timeout_add(1000, self.update_status_bar)  # Atualiza a cada segundo

        self.show_all()
        
    def create_menu_bar(self):
        # Cria o menu principal
        menu_bar = Gtk.MenuBar()
        # Menu Arquivo
        file_menu_item = Gtk.MenuItem(label="Arquivo")
        file_menu = Gtk.Menu()
        file_menu_item.set_submenu(file_menu)

        exit_item = Gtk.MenuItem(label="Sair")
        exit_item.connect("activate", self.on_exit_clicked)
        file_menu.append(exit_item)
        menu_bar.append(file_menu_item)

        # Menu Editar
        edit_menu_item = Gtk.MenuItem(label="Editar")
        edit_menu = Gtk.Menu()
        edit_menu_item.set_submenu(edit_menu)

        delete_item = Gtk.MenuItem(label="Excluir")
        delete_item.connect("activate", self.on_delete_clicked)
        edit_menu.append(delete_item)

        edit_item = Gtk.MenuItem(label="Editar")
        edit_item.connect("activate", self.on_edit_clicked)
        edit_menu.append(edit_item)
        menu_bar.append(edit_menu_item)

        # Menu Ver
        view_menu_item = Gtk.MenuItem(label="Ver")
        view_menu = Gtk.Menu()
        view_menu_item.set_submenu(view_menu)

        toggle_statusbar_item = Gtk.CheckMenuItem(label="Exibir Barra de Status")
        toggle_statusbar_item.set_active(True)
        toggle_statusbar_item.connect("toggled", self.on_toggle_statusbar)
        view_menu.append(toggle_statusbar_item)
        
        # Criar submenu "Ver"
        zoom_in_item = Gtk.MenuItem(label="Zoom In (Ctrl +)")
        zoom_in_item.connect("activate", self.on_zoom_in)
        view_menu.append(zoom_in_item)

        zoom_out_item = Gtk.MenuItem(label="Zoom Out (Ctrl -)")
        zoom_out_item.connect("activate", self.on_zoom_out)
        view_menu.append(zoom_out_item)
        
        menu_bar.append(view_menu_item)


        agenda_menu = Gtk.MenuItem(label="Agenda")
        # Submenu de "Agenda"
        agenda_submenu = Gtk.Menu()
        agenda_menu.set_submenu(agenda_submenu)
        calls_item = Gtk.MenuItem(label="Ligações")
        calls_item.connect("activate", self.on_agenda_clicked)
        agenda_submenu.append(calls_item)


        menu_bar.append(agenda_menu)

        doacao_menu = Gtk.MenuItem(label="Doações")
        doacao_menu.connect("activate", self.on_donations_clicked)

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
        
        # Menu Ajuda
        help_menu_item = Gtk.MenuItem(label="Ajuda")
        help_menu = Gtk.Menu()
        help_menu_item.set_submenu(help_menu)

        about_item = Gtk.MenuItem(label="Sobre")
        about_item.connect("activate", self.on_about_clicked)
        help_menu.append(about_item)
        menu_bar.append(help_menu_item)
        
        return menu_bar
    
    def on_exit_clicked(self, widget):
        """Fecha a aplicação."""
        self.close()

    def on_delete_clicked(self, widget):
        print("Excluir ação acionada!")

    def on_edit_clicked(self, widget):
        print("Editar ação acionada!")

    def on_toggle_statusbar(self, widget):
        """Mostra ou oculta a barra de status."""
        self.statusbar.set_visible(widget.get_active())

    def on_about_clicked(self, widget):
        """Exibe um diálogo sobre a aplicação usando Gtk.AboutDialog."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_program_name("Sistema Ebenezer")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("Sistema de gestão de doações.")
        about_dialog.set_website("https://www.exemplo.com")
        about_dialog.set_website_label("Visite nosso site")
        about_dialog.set_copyright("© 2024 Sistema Ebenezer")
        about_dialog.set_license("Licença MIT")
        about_dialog.set_wrap_license(True)
        about_dialog.set_authors(["Cezar Garrido Britez"])
        about_dialog.set_documenters(["Cezar Garrido Britez"])
        about_dialog.set_artists(["Cezar Garrido Britez"])
        about_dialog.set_logo_icon_name("help-about")  # Ícone padrão do sistema
        about_dialog.set_translator_credits("Indisponível")
        
        about_dialog.run()
        about_dialog.destroy()
        
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
            
    def remove_tab(self, title):
        """Remove a aba do notebook com o título especificado, se existir."""
        for i in range(self.notebook.get_n_pages()):
            tab_label = self.notebook.get_tab_label(self.notebook.get_nth_page(i))
            if tab_label is not None:
                label_widget = tab_label.get_children()[0]
                if isinstance(label_widget, Gtk.Label) and label_widget.get_text() == title:
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
        self.add_tab("Ligações", AgendaList(self.app))

    def on_donations_clicked(self, w):
        self.add_tab("Doações", DonationListForm(self.app))

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
    
    #TODO: Melhorar o Zoom
    def apply_css(self):
        """Aplica o CSS e força atualização dos componentes."""
        css = f"""
        window, label, button, menuitem, entry, notebook, statusbar {{
            font-size: {self.font_size}px;
        }}
        
        menuitem {{
             padding: 4px 10px; /* Ajusta espaçamento para não colapsar */
        }}
        """.encode("utf-8")

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        
    def on_zoom_in(self, widget=None):
        """Aumenta a fonte em +2 pontos."""
        self.font_size += 2
        self.apply_css()
        print(f"Zoom In: Fonte {self.font_size}px")

    def on_zoom_out(self, widget=None):
        """Diminui a fonte em -2 pontos."""
        if self.font_size > 14:  # Evita tamanho muito pequeno
            self.font_size -= 2
            self.apply_css()
            print(f"Zoom Out: Fonte {self.font_size}px")
            
    def add_keyboard_shortcuts(self):
        """Adiciona atalhos de teclado para Zoom In (Ctrl +) e Zoom Out (Ctrl -) usando lambda."""
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        # Atalho para Zoom In (Ctrl +)
        key, mod = Gtk.accelerator_parse("<Control>plus")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, lambda *args: self.on_zoom_in())

        # Atalho para Zoom Out (Ctrl -)
        key, mod = Gtk.accelerator_parse("<Control>minus")
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, lambda *args: self.on_zoom_out())
    def on_key_press(self, widget, event):
        """Captura atalhos de teclado manualmente para Zoom In e Zoom Out."""
        keyval = event.keyval
        state = event.state

        if state & Gdk.ModifierType.CONTROL_MASK:
            if keyval in (Gdk.KEY_plus, Gdk.KEY_equal):  # Captura Ctrl + ou Ctrl =
                self.on_zoom_in()
                return True
            elif keyval == Gdk.KEY_minus:  # Captura Ctrl -
                self.on_zoom_out()
                return True
        return False
