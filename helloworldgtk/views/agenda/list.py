import gi
from enum import Enum

from .form import EditAppointment
from .form import NewAppointment
from ...services.appointment_service import AppointmentService

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from datetime import datetime, timedelta

from ..tab import BaseTab

# Definição de Mensagens (Ações que podem ocorrer no sistema)
class Msg(Enum):
    LOAD_APPOINTMENTS = "load_appointments"
    DELETE_APPOINTMENT = "delete_appointment"
    SHOW_CONFIRMATION = "show_confirmation"
    SHOW_ERROR = "show_error"
    OPEN_NEW = "open_new"
    OPEN_EDIT = "open_edit"

class AgendaList(BaseTab):
    def __init__(self, app):
        self.app = app
        self.svc = AppointmentService()
        self.state = {"appointments": []}  # Estado inicial
        super().__init__()

    def create_content(self):
        """Cria o conteúdo da aba, incluindo o calendário e a lista de compromissos."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(hbox, True, True, 0)

        # Calendário
        self.calendar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.calendar_box.set_name("calendar-box")  # Nome para o CSS
        hbox.pack_start(self.calendar_box, False, True, 0)
        self.calendar = Gtk.Calendar()
        self.calendar.connect("day-selected", self.on_calendar_date_selected)
        self.calendar_box.pack_start(self.calendar, False, False, 0)

        # Lista de eventos
        
        # Lista de eventos e Toolbar
        event_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(event_box, True, True, 0)
        
        self.toolbar = Gtk.Toolbar()
        event_box.pack_start(self.toolbar, False, False, 0)
        
        self.prev_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_BACK)
        self.prev_button.connect("clicked", self.on_prev_clicked)

        self.toolbar.insert(self.prev_button, 0)
        
        self.date_label = Gtk.Label(label="")
        self.update_date_label()
        tool_item = Gtk.ToolItem()
        tool_item.add(self.date_label)
        self.toolbar.insert(tool_item, 2)
        
        self.next_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_FORWARD)
        self.next_button.connect("clicked", self.on_next_clicked)

        self.toolbar.insert(self.next_button, 3)
        
        self.event_store = Gtk.TreeStore(str, str, str, int)
        self.event_view = Gtk.TreeView(model=self.event_store)
        self.add_columns_to_event_view()
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.event_view)
        event_box.pack_start(scrolled_window, True, True, 0)
        

        self.handle_message(Msg.LOAD_APPOINTMENTS)
        self.apply_css()
        return vbox
    
    def on_prev_clicked(self, widget):
        """Retrocede um dia no calendário e atualiza a interface."""
        year, month, day = self.calendar.get_date()
        current_date = datetime(year, month + 1, day)
        new_date = current_date - timedelta(days=1)
        self.calendar.select_day(new_date.day)
        self.calendar.select_month(new_date.month - 1, new_date.year)
        self.update_date_label()
        self.handle_message(Msg.LOAD_APPOINTMENTS)

    def on_next_clicked(self, widget):
        """Avança um dia no calendário e atualiza a interface."""
        year, month, day = self.calendar.get_date()
        current_date = datetime(year, month + 1, day)
        new_date = current_date + timedelta(days=1)
        self.calendar.select_day(new_date.day)
        self.calendar.select_month(new_date.month - 1, new_date.year)
        self.update_date_label()
        self.handle_message(Msg.LOAD_APPOINTMENTS)

    def update_date_label(self):
        """Atualiza o texto da label de data com a data atualmente selecionada."""
        year, month, day = self.calendar.get_date()
        selected_date = datetime(year, month + 1, day)
        self.date_label.set_text(selected_date.strftime("%d de %B de %Y"))

    def apply_css(self):
        """Aplica estilo CSS ao calendário."""
        css = b"""
        #calendar-box {
            background-color: @theme_bg_color;
            padding: 10px;
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def add_columns_to_event_view(self):
        """Adiciona colunas ao TreeView."""
        renderer = Gtk.CellRendererText()
        self.event_view.append_column(Gtk.TreeViewColumn("Hora / Obs.", renderer, text=0))
        self.event_view.append_column(Gtk.TreeViewColumn("Doador", renderer, text=1))
        
    def on_calendar_date_selected(self, widget):
        
        """Atualiza a label da data ao selecionar um novo dia no calendário."""
        self.update_date_label()
        self.handle_message(Msg.LOAD_APPOINTMENTS)
        
    def handle_message(self, msg, data=None):
        """Processa mensagens e executa ações conforme necessário."""
        print(f"Handling message: {msg}")
        if msg == Msg.LOAD_APPOINTMENTS:
            print("Loading appointments...")
            self.load_appointments()
        elif msg == Msg.DELETE_APPOINTMENT:
            self.delete_appointment(data)
        elif msg == Msg.SHOW_CONFIRMATION:
            return self.show_confirmation_dialog(data)
        elif msg == Msg.SHOW_ERROR:
            self.show_error_dialog(data)
        elif msg == Msg.OPEN_NEW:
            form = NewAppointment(self.app, self.get_toplevel())
            form.connect("appointment_saved", lambda _, __: self.handle_message(Msg.LOAD_APPOINTMENTS))
        elif msg == Msg.OPEN_EDIT:
            self.edit_appointment()

    def load_appointments(self):
        """Carrega compromissos para a data selecionada."""
        print("carregando...")
        year, month, day = self.calendar.get_date()
        selected_date = datetime(year, month + 1, day).date()
        print(f"Selected date: {selected_date}")
        self.state["appointments"].clear()
        self.state["appointments"] = self.svc.get_appointments_by_date(self.app.logged_user, selected_date)
        self.update_event_view(self.state["appointments"])


    def update_event_view(self, appointments):
        """Atualiza a lista de eventos na interface."""
        self.event_store.clear()
        grouped_appointments = {}
        for appointment in appointments:
            hour_exact = f"{appointment.time[:2]}:00" if appointment.time else "Sem horário"
            donor_name = appointment.calls.donor.name if appointment.calls else "N/A"
            grouped_appointments.setdefault(hour_exact, []).append((appointment.time, appointment.notes or "N/A", donor_name, appointment.id))
        
        for hour_group, events in sorted(grouped_appointments.items()):
            parent = self.event_store.append(None, [hour_group, "", "", -1])
            
            for full_time, event_desc, donor, appointment_id in sorted(events):
                self.event_store.append(parent, [f"{full_time} - {event_desc}", donor, "", appointment_id])
                
            self.event_view.expand_row(self.event_store.get_path(parent), True)
            
    def delete_appointment(self, appointment_id):
        """Tenta excluir um compromisso."""
        if appointment_id == -1:
            self.handle_message(Msg.SHOW_ERROR, "Nenhum compromisso selecionado.")
            return
        if self.handle_message(Msg.SHOW_CONFIRMATION, "Deseja realmente excluir este compromisso?"):
            self.svc.deactivate(self.app.logged_user, appointment_id)
            self.handle_message(Msg.LOAD_APPOINTMENTS)

    def edit_appointment(self):
        """Abre a tela de edição de compromisso."""
        selection = self.event_view.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter:
            appointment_id = model[tree_iter][3]
            if appointment_id == -1:
                self.handle_message(Msg.SHOW_ERROR, "Nenhum compromisso selecionado.")
                return
            form = EditAppointment(self.app, self.get_toplevel(), appointment_id)
            form.connect("appointment_saved", lambda _, __: self.handle_message(Msg.LOAD_APPOINTMENTS))
        else:
            self.handle_message(Msg.SHOW_ERROR, "Nenhum compromisso selecionado.")

    def get_toolbar_actions(self):
        """Define os botões da toolbar."""
        return [
            ("new", "document-new", "Novo", lambda _: self.handle_message(Msg.OPEN_NEW)),
            ("edit", "document-edit", "Editar", lambda _: self.handle_message(Msg.OPEN_EDIT)),
            ("delete", "edit-delete", "Excluir", lambda _: self.handle_message(Msg.DELETE_APPOINTMENT, self.get_selected_appointment_id())),
            None,
            ("close", "window-close", "Fechar", lambda _: self.destroy()),
        ]

    def get_selected_appointment_id(self):
        """Retorna o ID do compromisso selecionado."""
        selection = self.event_view.get_selection()
        model, tree_iter = selection.get_selected()
        return model[tree_iter][3] if tree_iter else -1
    
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
    
    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Erro!",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()