import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from helloworldgtk.services.donor_service import DonorService  # Importa o serviço de doadores
from ...models.user import User

class DonorSearchDialog(Gtk.Dialog):
    def __init__(self, parent, user: User):
        super().__init__(title="Buscar Doadores", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.set_default_size(300, 100)
        self.user = user
        self.service = DonorService()
        self.donor_map = {}  # Dicionário para armazenar os objetos Donor

        box = self.get_content_area()

        # Campo de entrada para busca
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Digite o nome do doador...")
        self.search_entry.connect("changed", self.on_search_changed)
        search_box.pack_start(self.search_entry, True, True, 0)
        box.add(search_box)

        # Modelo para armazenar os doadores (ID, Nome)
        self.liststore = Gtk.ListStore(int, str, str)
        self.update_list("")  # Carrega a lista inicial

        # Criando a TreeView
        self.treeview = Gtk.TreeView(model=self.liststore)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("ID", renderer, text=0)
        self.treeview.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Nome", renderer, text=1)
        self.treeview.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Telefones", renderer, text=2)
        self.treeview.append_column(column)

        box.add(self.treeview)

        self.show_all()

    def update_list(self, search_term):
        """ Atualiza a lista de doadores filtrando pelo nome. """
        self.liststore.clear()
        self.donor_map.clear()  # Limpa o dicionário de doadores
        
        donors = self.service.search(self.user, search_term)
        for donor in donors:
            phones = ", ".join(contact.phone for contact in donor.contacts)
            self.liststore.append([donor.id, donor.name, phones])
            self.donor_map[donor.id] = donor  # Armazena o objeto completo

    def on_search_changed(self, widget):
        """ Chamado quando o usuário digita no campo de busca. """
        search_term = self.search_entry.get_text()
        self.update_list(search_term)

    def get_selected_donor(self):
        """ Retorna o objeto Donor selecionado. """
        selection = self.treeview.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter is not None:
            donor_id = model[tree_iter][0]  # Obtém o ID do doador
            return self.donor_map.get(donor_id)  # Retorna o objeto Donor completo
        return None
