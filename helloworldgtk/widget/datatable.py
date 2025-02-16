import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class DataTable(Gtk.Box):
    def __init__(self, columns, fetch_data_function, column_formatters=None, rows_per_page_options=None):
        """
        Cria um DataTable reutilizável com paginação, busca e ordenação.

        :param columns: Lista de colunas (ex: [("ID", int), ("Nome", str)])
        :param fetch_data_function: Função que recebe (search_term, offset, limit) e retorna os dados.
        :param column_formatters: Dicionário de formatadores de colunas, ex: {"Status": format_status}
        :param rows_per_page_options: Lista de opções para registros por página (ex: [10, 25, 50])
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)

        self.columns = columns
        self.fetch_data_function = fetch_data_function
        self.column_formatters = column_formatters or {}
        self.items_per_page = 10
        self.current_page = 0
        self.total_pages = 1
        self.search_term = ""

        # Campo de busca
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Buscar...")
        self.search_entry.connect("changed", self.on_search)
        self.pack_start(self.search_entry, False, False, 5)

        # Criando área de rolagem para a tabela
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scrolled_window, True, True, 5)

        # Criando modelo de dados
        self.store = Gtk.ListStore(*[col_type for _, col_type in columns])

        # Criando TreeView com modelo de dados
        self.treeview = Gtk.TreeView(model=self.store)
        scrolled_window.add(self.treeview)

        # Criando colunas dinamicamente com suporte a formatadores
        for index, (title, col_type) in enumerate(columns):
            self.add_column(title, index)

        # Criando container para paginação e seleção de registros por página
        pagination_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        pagination_container.set_halign(Gtk.Align.END)  # Alinha à direita
        self.pack_start(pagination_container, False, False, 5)

        # Criando dropdown para selecionar quantos registros por página
        self.rows_per_page_dropdown = Gtk.ComboBoxText()
        self.rows_per_page_options = rows_per_page_options or [10, 25, 50, 100]

        for num in self.rows_per_page_options:
            self.rows_per_page_dropdown.append_text(str(num))
        self.rows_per_page_dropdown.set_active(0)
        self.rows_per_page_dropdown.connect("changed", self.on_rows_per_page_changed)

        rows_label = Gtk.Label(label="Registros por página:")
        pagination_container.pack_start(rows_label, False, False, 0)
        pagination_container.pack_start(self.rows_per_page_dropdown, False, False, 0)

        # Criando botões de paginação
        self.pagination_box = Gtk.Box(spacing=6)
        pagination_container.pack_start(self.pagination_box, False, False, 0)

        # Carregar os dados iniciais
        self.load_data()

    def add_column(self, title, column_id):
        """Adiciona uma coluna ordenável à TreeView, aplicando formatadores se necessário."""
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=column_id)

        # Se existir um formatador para essa coluna, aplica a função
        if title in self.column_formatters:
            column.set_cell_data_func(renderer, self.column_formatters[title], None)

        column.set_sort_column_id(column_id)
        column.set_clickable(True)
        self.treeview.append_column(column)

    def load_data(self):
        """Carrega os dados chamando a função `fetch_data_function` com paginação."""
        offset = self.current_page * self.items_per_page

        # Busca os dados usando a função fornecida
        data, total_records = self.fetch_data_function(self.search_term, offset, self.items_per_page)

        # Atualiza o número total de páginas
        self.total_pages = max(1, (total_records // self.items_per_page) + (1 if total_records % self.items_per_page else 0))

        # Atualiza os dados na tabela
        self.store.clear()
        for row in data:
            self.store.append(row)

        # Atualiza os botões de paginação
        self.update_pagination_buttons()
        
    def update_pagination_buttons(self):
        """Atualiza os botões de paginação corretamente."""
        for child in self.pagination_box.get_children():
            self.pagination_box.remove(child)

        # Criar botões de navegação
        self.first_button = Gtk.Button(label="«")
        self.first_button.connect("clicked", self.on_first_page)

        self.prev_button = Gtk.Button(label="‹")
        self.prev_button.connect("clicked", self.on_prev_page)

        self.next_button = Gtk.Button(label="›")
        self.next_button.connect("clicked", self.on_next_page)

        self.last_button = Gtk.Button(label="»")
        self.last_button.connect("clicked", self.on_last_page)

        # Adiciona os botões
        self.pagination_box.pack_start(self.first_button, False, False, 0)
        self.pagination_box.pack_start(self.prev_button, False, False, 0)
        self.pagination_box.pack_start(self.next_button, False, False, 0)
        self.pagination_box.pack_start(self.last_button, False, False, 0)

        # Ativa/desativa botões conforme necessário
        self.first_button.set_sensitive(self.current_page > 0)
        self.prev_button.set_sensitive(self.current_page > 0)
        self.next_button.set_sensitive(self.current_page < self.total_pages - 1)
        self.last_button.set_sensitive(self.current_page < self.total_pages - 1)

        self.pagination_box.show_all()
    def on_rows_per_page_changed(self, combo):
        """Atualiza a quantidade de registros por página."""
        self.items_per_page = int(combo.get_active_text())
        self.current_page = 0
        self.load_data()

    def on_search(self, entry):
        """Filtra os resultados chamando a função `fetch_data_function` com o termo de busca."""
        self.search_term = entry.get_text().strip().lower()
        self.current_page = 0
        self.load_data()

    def on_first_page(self, button):
        self.current_page = 0
        self.load_data()

    def on_prev_page(self, button):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()

    def on_next_page(self, button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_data()

    def on_last_page(self, button):
        self.current_page = self.total_pages - 1
        self.load_data()
        
    def get_selected_row(self):
        """Retorna a linha selecionada no TreeView."""
        selection = self.treeview.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter:
            return [model.get_value(tree_iter, i) for i in range(len(self.columns))]
        return None  # Nenhuma linha selecionada
