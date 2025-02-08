from gi import require_versions

from .views.user.list import UserList
require_versions({"Gtk": "3.0", "Poppler": "0.18"})
from gi.repository import Gtk, Poppler

class Window(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)
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
        menu_bar.append(agenda_menu)

        # Menu "Cadastros"
        cadastros_menu = Gtk.MenuItem(label="Cadastros")
        menu_bar.append(cadastros_menu)

        # Submenu de "Cadastros"
        cadastros_submenu = Gtk.Menu()
        cadastros_menu.set_submenu(cadastros_submenu)

        # Submenu "Funcionários"
        funcionarios_item = Gtk.MenuItem(label="Funcionários")
        funcionarios_item.connect("activate", self.on_funcionarios_clicked)
        cadastros_submenu.append(funcionarios_item)

        # Submenu "Usuários"
        usuarios_item = Gtk.MenuItem(label="Usuários")
        usuarios_item.connect("activate", self.on_usuarios_clicked)
        cadastros_submenu.append(usuarios_item)

        about_menu = Gtk.MenuItem(label="Sobre")
        menu_bar.append(about_menu)
        # Adiciona o menu à caixa principal
        vbox.pack_start(menu_bar, False, False, 0)

        # Barra de ferramentas
        toolbar = Gtk.Toolbar()
        
        # Botões da barra de ferramentas
        self.add_tool_button(toolbar, "Salvar", "document-save", self.on_new_clicked)
        self.add_tool_button(toolbar, "Fechar", "window-close", self.on_new_clicked)
        separator = Gtk.SeparatorToolItem()
        toolbar.insert(separator, -1)
    
        self.add_tool_button(toolbar, "Novo", "document-new", self.on_new_clicked)
        self.add_tool_button(toolbar, "Abrir", "document-open", self.on_open_clicked)
        
        separator = Gtk.SeparatorToolItem()
        toolbar.insert(separator, -1)
    

        self.add_tool_button(toolbar, "Editar", "document-edit", self.on_add_event_clicked)
        self.add_tool_button(toolbar, "Excluir", "edit-delete", self.on_remove_event_clicked)


        vbox.pack_start(toolbar, False, False, 0)

        # Cria o notebook (tabsheet)
        self.notebook = Gtk.Notebook()
        vbox.pack_start(self.notebook, True, True, 0)

        # Inicializa com a aba padrão
        self.add_tab("Bem-vindo", Gtk.Label(label="Selecione um cadastro no menu para começar."))

        # Cria a barra de status
        self.status_bar = Gtk.Statusbar()
        
        vbox.pack_end(self.status_bar, False, False, 0)

        # ID do contexto para mensagens na barra de status
        self.context_id = self.status_bar.get_context_id("status")

        # Mensagem inicial na status bar
        self.update_status(f"Usuário: Cezar Garrido | Hora: {self.get_current_time()}")

        self.connect("destroy", Gtk.main_quit)  # Fecha o aplicativo ao fechar a janela
        self.show_all()

    def add_tool_button(self, toolbar, label, icon_name, callback):
            """Adiciona um botão à barra de ferramentas com ícone."""
            button = Gtk.ToolButton()
            image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.SMALL_TOOLBAR)
            button.set_icon_widget(image)
            toolbar.set_style(Gtk.ToolbarStyle.BOTH)
            button.set_label(label)
            button.set_tooltip_text(label)
            button.connect("clicked", callback)
            toolbar.insert(button, -1)

    def add_tab(self, title, content):
        """Adiciona uma aba ao notebook com o título e conteúdo especificados."""
        # Verifica se a aba já existe
        for i in range(self.notebook.get_n_pages()):
            tab_label = self.notebook.get_tab_label(self.notebook.get_nth_page(i))
            if isinstance(tab_label, Gtk.Box):  # Certifica-se de que é um Box
                label = tab_label.get_children()[0]  # Primeiro filho é o Gtk.Label
                if isinstance(label, Gtk.Label) and label.get_text() == title:
                    self.notebook.set_current_page(i)
                    return
        # Cria o botão de fechar
        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.set_focus_on_click(False)
        close_button.add(Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.SMALL_TOOLBAR))
        close_button.connect("clicked", self.on_close_tab_clicked)

        # Cria o título com botão de fechar
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        title_box.pack_start(Gtk.Label(label=title), True, True, 0)
        title_box.pack_start(close_button, False, False, 0)
        title_box.show_all()

        # Adiciona a aba ao notebook
        self.notebook.append_page(content, title_box)
        self.notebook.set_current_page(self.notebook.get_n_pages() - 1)

    def on_close_tab_clicked(self, button):
        """Fecha a aba correspondente ao botão de fechar."""
        for i in range(self.notebook.get_n_pages()):
            tab_label = self.notebook.get_tab_label(self.notebook.get_nth_page(i))
            if tab_label is not None and button in tab_label.get_children():
                self.notebook.remove_page(i)
                break

    def on_funcionarios_clicked(self, widget):
        print("Submenu Funcionários clicado!")
        self.update_status("Menu Funcionários selecionado.")
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content.pack_start(UserList(), True, True, 0)
        content.show_all()

        self.add_tab("Funcionários", content)

    def on_usuarios_clicked(self, widget):
        print("Submenu Usuários clicado!")
        self.update_status("Menu Usuários selecionado.")
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content.pack_start(Gtk.Label(label="Cadastro de Usuários"), True, True, 0)
        content.pack_start(Gtk.Entry(placeholder_text="Nome de Usuário"), False, False, 0)
        content.pack_start(Gtk.Entry(placeholder_text="Senha"), False, False, 0)
        content.show_all()
        self.add_tab("Usuários", content)

    def update_status(self, message):
        """Atualiza a mensagem na status bar."""
        self.status_bar.push(self.context_id, message)
   
    def get_current_time(self):
        """Obtém a hora atual formatada."""

    # Callbacks para os botões da barra de ferramentas
    def on_new_clicked(self, widget):
        print("New clicked!")

    def on_open_clicked(self, widget):
        print("Open clicked!")

    def on_add_event_clicked(self, widget):
        # Exemplo de evento
        self.event_store.append(["Sample Event", "Location A", "10:00 AM"])
        print("Event added!")

    def on_remove_event_clicked(self, widget):
        selection = self.event_view.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter:
            model.remove(tree_iter)
            print("Event removed!")

    def on_clear_all_clicked(self, widget):
        self.event_store.clear()
        print("All events cleared!")