import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from helloworldgtk.services.donor_service import DonorService
from ...models.user import User

class DonorSearchDialog(Gtk.Dialog):
    PAGE_SIZE = 10  # Número de doadores por página

    def __init__(self, parent, user: User):
        super().__init__(title="Buscar Doadores", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.set_default_size(300, 300)
        self.user = user
        self.service = DonorService()
        self.donor_map = {}
        self.offset = 0
        self.current_search = ""

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        
        # Campo de entrada para busca
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Digite o nome do doador...")
        self.search_entry.connect("changed", self.on_search_changed)
        search_box.pack_start(self.search_entry, True, True, 0)
        box.pack_start(search_box, False, False, 0)

        # Modelo para armazenar os doadores (ID, Nome)
        self.liststore = Gtk.ListStore(int, str, str)

        # Criando a TreeView
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.connect("key-press-event", self.on_treeview_key_pressed)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("ID", renderer, text=0)
        self.treeview.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Nome", renderer, text=1)
        self.treeview.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Telefones", renderer, text=2)
        self.treeview.append_column(column)

        box.pack_start(self.treeview, True, True, 0)

        # Criar botões de navegação ANTES de chamar update_list()
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.prev_button = Gtk.Button(label="Anterior")
        self.prev_button.connect("clicked", self.on_prev_clicked)
        self.prev_button.set_sensitive(False)

        self.next_button = Gtk.Button(label="Próximo")
        self.next_button.connect("clicked", self.on_next_clicked)

        nav_box.pack_start(self.prev_button, True, True, 0)
        nav_box.pack_start(self.next_button, True, True, 0)
        box.pack_start(nav_box, False, False, 0)

        self.get_content_area().add(box)

        # Agora que tudo está inicializado, podemos chamar update_list()
        self.update_list()

        self.show_all()

    def update_list(self):
        """ Atualiza a lista de doadores com paginação. """
        self.liststore.clear()
        self.donor_map.clear()

        donors = self.service.search(self.user, self.current_search, self.offset, self.PAGE_SIZE)
        for donor in donors:
            phones = ", ".join(contact.phone for contact in donor.contacts)
            self.liststore.append([donor.id, donor.name, phones])
            self.donor_map[donor.id] = donor

        # Atualiza estado dos botões
        self.prev_button.set_sensitive(self.offset > 0)
        self.next_button.set_sensitive(len(donors) == self.PAGE_SIZE)

    def on_search_changed(self, widget):
        """ Reinicia a busca e reseta a paginação. """
        self.current_search = self.search_entry.get_text()
        if self.current_search == "":
            self.current_search = None
        self.offset = 0
        self.update_list()

    def on_prev_clicked(self, widget):
        """ Exibe a página anterior. """
        if self.offset >= self.PAGE_SIZE:
            self.offset -= self.PAGE_SIZE
            self.update_list()

    def on_next_clicked(self, widget):
        """ Exibe a próxima página. """
        self.offset += self.PAGE_SIZE
        self.update_list()

    def get_selected_donor(self):
        """ Retorna o objeto Donor selecionado. """
        selection = self.treeview.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter is not None:
            donor_id = model[tree_iter][0]
            return self.donor_map.get(donor_id)
        return None

    def on_treeview_key_pressed(self, widget, event):
        """ Captura o evento de tecla pressionada na TreeView. """
        if event.keyval == Gdk.KEY_Return:
            selected_donor = self.get_selected_donor()
            if selected_donor:
                self.response(Gtk.ResponseType.OK)
