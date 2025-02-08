
from gi.repository import Gtk
# =======================
# Classe Base para as Abas
# =======================
class BaseTab(Gtk.Box):
    """Classe base para abas que define um conteúdo e suas ações de toolbar."""
    """Classe base para abas do sistema, fornecendo estrutura para conteúdo e toolbar."""
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Criando o conteúdo principal da aba
        content = self.create_content()
        self.pack_start(content, True, True, 0)

        self.show_all()

    def get_toolbar_actions(self):
        """Deve retornar uma lista de ações para a toolbar."""
        raise NotImplementedError("Cada aba deve definir suas ações de toolbar")

    def create_content(self):
        """Deve retornar o conteúdo principal da aba."""
        raise NotImplementedError("Cada aba deve definir seu conteúdo")

class WelcomeTab(BaseTab):
    def __init__(self):
        super().__init__()

    def get_toolbar_actions(self):
        """Retorna as ações específicas da toolbar para esta aba."""
        return []

    def create_content(self):
        """Cria o conteúdo principal da aba de boas-vindas."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        label = Gtk.Label(label="Bem-vindo ao Sistema!")
        label.set_markup("<span size='xx-large' weight='bold'>Bem-vindo ao Sistema!</span>")
        label.set_justify(Gtk.Justification.CENTER)

        desc_label = Gtk.Label(label="Selecione uma das abas acima para começar.")
        desc_label.set_justify(Gtk.Justification.CENTER)

        box.pack_start(label, True, True, 0)
        box.pack_start(desc_label, True, True, 0)
        return box