import gi
from helloworldgtk.models.appointment import Appointment, AppointmentCall
from helloworldgtk.services.appointment_service import AppointmentService
from helloworldgtk.views.donor.search import DonorSearchDialog

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import datetime
import subprocess

class EditAppointment(Gtk.Window):
    __gsignals__ = {
        "appointment_updated": (GObject.SignalFlags.RUN_FIRST, None, (int,)),  # Agora aceita um argumento tipo str
    }
    
    def __init__(self, app, parent, id):
        Gtk.Window.__init__(self, title="Editar Compromisso")
        self.set_default_size(350, 550)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_vexpand(False)

        self.app = app
        self.appointment_id = id

        self.connect('destroy', self.quit_window)

        # Contêiner principal
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_vbox.set_border_width(10)

        # Scrolled box para os campos do formulário
        scrolled_box = Gtk.ScrolledWindow()
        scrolled_box.set_hexpand(True)
        scrolled_box.set_vexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Descrição
        box.pack_start(Gtk.Label(label='Descrição:', xalign=0), False, False, 0)
        self.task_field = Gtk.Entry()
        box.pack_start(self.task_field, False, False, 0)

        # Doador
        box.pack_start(Gtk.Label(label='Doador:', xalign=0), False, False, 0)
        self.donor_entry = Gtk.Entry(editable=False)
        self.donor_entry.connect("button-press-event", self.on_donor_entry_clicked)
        box.pack_start(self.donor_entry, False, False, 0)

        # Telefones
        box.pack_start(Gtk.Label(label='Telefones:', xalign=0), False, False, 0)
        self.phone_listbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.pack_start(self.phone_listbox, False, False, 0)

        add_phone_button = Gtk.Button(label="Adicionar Telefone")
        add_phone_button.connect("clicked", self.add_phone)
        box.pack_start(add_phone_button, False, False, 0)

        # Calendário
        self.cal = Gtk.Calendar()
        box.pack_start(self.cal, False, False, 0)

        # Horário
        time_hbox = Gtk.Box()
        self.hours_field = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 23, 1, 10, 0))
        self.minutes_field = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 59, 1, 10, 0))
        time_hbox.pack_start(self.hours_field, False, False, 0)
        time_hbox.pack_start(Gtk.Label(label=' : '), False, False, 0)
        time_hbox.pack_start(self.minutes_field, False, False, 0)
        box.pack_start(time_hbox, False, False, 0)

        # Anotações
        box.pack_start(Gtk.Label(label='Anotações:', xalign=0), False, False, 0)
        self.textview = Gtk.TextView()
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(False)
        scrolled_window.add(self.textview)
        box.pack_start(scrolled_window, False, False, 0)

        # Adiciona a caixa de rolagem ao contêiner principal
        scrolled_box.add(box)
        main_vbox.pack_start(scrolled_box, True, True, 0)

        # Botão Salvar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_set_alarm = Gtk.Button(label="Salvar")
        button_set_alarm.connect('clicked', self.button_set_alarm_clicked)
        button_box.pack_end(button_set_alarm, False, False, 0)

        # Adiciona a caixa de botões ao layout principal
        main_vbox.pack_start(button_box, False, False, 0)

        # Adiciona tudo à janela
        self.add(main_vbox)
        self.load_appointment()

        self.show_all()

    def load_appointment(self):
        svc = AppointmentService()

        appointment = svc.get_by_id(self.app.logged_user, self.appointment_id)
        if appointment:
            self.task_field.set_text("")
            self.selected_donor = appointment.calls.donor
            self.donor_entry.set_text(appointment.calls.donor.name if appointment.calls.donor else "")
            
            for phone in appointment.calls.phone.split(","):
                self.add_phone(None, phone)

            self.cal.select_day(appointment.date.day)
            self.cal.select_month(appointment.date.month - 1, appointment.date.year)
            
            hours, minutes = map(int, appointment.time.split(':'))
            self.hours_field.set_value(hours)
            self.minutes_field.set_value(minutes)
            
            buffer = self.textview.get_buffer()
            buffer.set_text(appointment.notes)
        self.appointment = appointment

    def add_phone(self, widget, phone_number=""):
        phone_entry = Gtk.Entry()
        phone_entry.set_text(phone_number)
        delete_button = Gtk.Button(label="Excluir")

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.pack_start(phone_entry, True, True, 0)
        hbox.pack_start(delete_button, False, False, 0)

        self.phone_listbox.pack_start(hbox, False, False, 0)
        self.phone_listbox.show_all()

        delete_button.connect("clicked", self.delete_phone, hbox)

    def save_phone(self, widget, phone_entry):
        phone_entry.set_editable(False)

    def delete_phone(self, widget, hbox):
        self.phone_listbox.remove(hbox)

    def on_donor_entry_clicked(self, widget, event):
        dialog = DonorSearchDialog(self, self.app.logged_user)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.selected_donor = dialog.get_selected_donor()
            if self.selected_donor:
                self.donor_entry.set_text(self.selected_donor.name)
                self.populate_phones(self.selected_donor.contacts)
        dialog.destroy()

    def populate_phones(self, contacts):
        for child in self.phone_listbox.get_children():
            self.phone_listbox.remove(child)
        for contact in contacts:
            self.add_phone(None, contact.phone)

    def button_set_alarm_cliked(self, button):
        task_description = self.task_field.get_text()
        self.destroy()

    def quit_window(self, window):
        self.destroy()
        
    def button_set_alarm_clicked(self, button):
        # Capturar dados do formulário
        task_description = self.task_field.get_text()
        donor = self.selected_donor
        if not donor:
            print("Erro: Nenhum doador selecionado.")
            return
       # Salvar no banco de dados
        try:
            # Capturar data e hora
            year, month, day = self.cal.get_date()
            selected_date = datetime.datetime(year, month + 1, day)           
            hours = self.hours_field.get_value_as_int()
            minutes = self.minutes_field.get_value_as_int()
            selected_time = f"{hours:02d}:{minutes:02d}"

            # Capturar anotações
            buffer = self.textview.get_buffer()
            start_iter, end_iter = buffer.get_bounds()
            notes = buffer.get_text(start_iter, end_iter, True)

            # Criar novo compromisso
            
            self.appointment.date=selected_date
            self.appointment.time=selected_time
            self.appointment.event_type='Ligação'
            self.appointment.notes=notes
            
            # Capturar a lista de telefones
            phone_numbers = []
            for hbox in self.phone_listbox.get_children():
                for child in hbox.get_children():
                    if isinstance(child, Gtk.Entry):
                        phone_numbers.append(child.get_text().strip())

            phone_numbers_str = ",".join(phone_numbers)  # Converte a lista para string separada por vírgulas

            self.appointment.calls.phone = phone_numbers_str
     
            svc = AppointmentService()
            id = svc.update(self.app.logged_user, self.appointment)
            print("Compromisso salvo com sucesso! {}", id)
            self.destroy()
        except Exception as e:
            print(f"Erro ao salvar compromisso: {e}")
