import gi
from datetime import datetime

from .new import NewAppointment
from ...services.appointment_service import AppointmentService

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..tab import BaseTab

class AgendaList(BaseTab):
    def __init__(self, app):
        """
        Inicializa a aba de listagem de compromissos.
        :param app: Instância da Application, usada para obter o usuário logado.
        """
        self.app = app  # Guarda a instância da aplicação
        self.svc = AppointmentService()
        super().__init__()

    def create_content(self):
        """Cria o conteúdo da aba, que consiste em um calendário e uma lista de eventos agrupados por hora."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Caixa horizontal para o calendário e lista de eventos
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        # Calendário
        self.calendar = Gtk.Calendar()
        self.calendar.connect("day-selected", self.on_date_selected)  # Atualiza eventos ao mudar a data
        hbox.pack_start(self.calendar, False, False, 0)

        # Lista de eventos com agrupamento
        self.event_store = Gtk.TreeStore(str, str, str)  # 3 colunas: Hora/Descrição, Nome do Evento, Doador
        self.event_view = Gtk.TreeView(model=self.event_store)
        self.add_columns_to_event_view()

        # ScrolledWindow para a lista de eventos
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.event_view)
        hbox.pack_start(scrolled_window, True, True, 0)

        # Carregar eventos do dia atual ao abrir a aba
        self.load_appointments_for_selected_date()

        return vbox

    def add_columns_to_event_view(self):
        """Adiciona colunas à lista de eventos com agrupamento."""
        renderer = Gtk.CellRendererText()

        column_desc = Gtk.TreeViewColumn("Descrição / Hora", renderer, text=0)
        self.event_view.append_column(column_desc)

        column_donor = Gtk.TreeViewColumn("Doador", renderer, text=1)
        self.event_view.append_column(column_donor)

    def load_appointments_for_selected_date(self):
        """Carrega os compromissos do banco para a data selecionada no calendário, agrupando por hora cheia."""
        # Obtém a data selecionada no calendário
        year, month, day = self.calendar.get_date()
        selected_date = datetime(year, month + 1, day).date()

        print(f"Data selecionada: {selected_date}")

        # Busca os compromissos na base de dados
        appointments = self.svc.get_appointments_by_date(self.app.logged_user, selected_date)

        # Limpa a árvore antes de inserir novos dados
        self.event_store.clear()

        # Agrupar compromissos por hora cheia (ex: "01:00", "02:00")
        grouped_appointments = {}
        for appointment in appointments:
            if appointment.time:
                full_time = appointment.time.strip()  # Exemplo: "14:35"
                hour_exact = full_time[:2] + ":00"  # Transforma em "14:00"
            else:
                full_time = "Sem horário"
                hour_exact = "Sem horário"

            donor_name = appointment.calls.donor.name if appointment.calls else "N/A"
            
            print(f"Compromisso: {appointment.notes or 'Sem descrição'}, Hora: {full_time}, Grupo: {hour_exact}, Doador: {donor_name}")

            if hour_exact not in grouped_appointments:
                grouped_appointments[hour_exact] = []

            grouped_appointments[hour_exact].append((full_time, appointment.notes or "Sem descrição", donor_name))

        # Adiciona os dados à árvore
        for hour_group, events in sorted(grouped_appointments.items()):
            print(f"Adicionando hora cheia: {hour_group}")
            parent = self.event_store.append(None, [hour_group, "", ""])  # Nó pai com a hora cheia

            # Ordena os eventos dentro do grupo por minuto
            for full_time, event_desc, donor in sorted(events):
                print(f"Adicionando evento: {event_desc}, Hora: {full_time}, Doador: {donor}")
                self.event_store.append(parent, [f"🟢 {full_time} - {event_desc}", donor, ""])  # Nó filho com detalhes do compromisso
            
            self.event_view.expand_row(self.event_store.get_path(parent), True)


    def get_toolbar_actions(self):
        """Define os botões da toolbar."""
        return [
            ("new", "document-new", "Novo", self.on_new_clicked),
            ("edit", "document-edit", "Editar", self.on_edit_clicked),
            ("delete", "edit-delete", "Desativar", self.on_delete_clicked),
            None,  # Separador
            ("close", "window-close", "Fechar", self.on_close_clicked),
        ]
    
    def on_date_selected(self, calendar):
        """Atualiza a lista de eventos ao selecionar uma nova data no calendário."""
        self.load_appointments_for_selected_date()

    def on_new_clicked(self, action):
        """Abre a tela de novo compromisso."""
        form = NewAppointment(self.app, self.get_toplevel())

    def on_edit_clicked(self, action):
        """Edita o compromisso selecionado."""
        selection = self.event_view.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter:
            appointment_id = model[tree_iter][0]  # Obtém o ID do compromisso
            print(f"Editar compromisso ID {appointment_id}")  # Implementar edição depois

    def on_delete_clicked(self, action):
        """Deleta o compromisso selecionado."""
        selection = self.event_view.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter:
            appointment_id = model[tree_iter][0]
            confirm = self.show_confirmation_dialog("Deseja realmente excluir este compromisso?")
            if confirm:
                self.svc.delete_appointment(appointment_id)
                self.load_appointments_for_selected_date()

    def on_close_clicked(self, action):
        """Fecha a aba de agenda."""
        self.get_toplevel().destroy()

    def show_confirmation_dialog(self, message):
        """Exibe um diálogo de confirmação e retorna True se o usuário confirmar."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=message,
        )
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES
