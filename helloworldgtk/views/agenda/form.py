import locale
import gi
from helloworldgtk.models.appointment import Appointment, AppointmentCall
from helloworldgtk.services.donation_service import DonationService
from helloworldgtk.services.appointment_service import AppointmentService
from helloworldgtk.views.donor.search import DonorSearchDialog
from helloworldgtk.widget.pdf_viewer import PDFViewer
from helloworldgtk.widget.validate_entry import FormValidator
from helloworldgtk.views.donation.new import NewForm as DonationNewForm

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GObject, Gdk
import datetime

class AppointmentBase(Gtk.Window):
    __gsignals__ = {
        "appointment_saved": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    def __init__(self, app, parent, title):
        Gtk.Window.__init__(self, title=title)
        self.set_default_size(350, 500)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_vexpand(False)

        self.app = app
        self.new_donation = None
        self.selected_donor = None
        self.connect('destroy', self.quit_window)
        self.v = FormValidator()

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_vbox.set_border_width(10)
        
        scrolled_box = Gtk.ScrolledWindow()
        scrolled_box.set_hexpand(True)
        scrolled_box.set_vexpand(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.donor_entry = self.v.add("Doador:")
        self.donor_entry.entry.set_editable(False)
        self.donor_entry.entry.connect("button-press-event", self.on_donor_entry_clicked)
        box.pack_start(self.donor_entry, False, False, 0)

        box.pack_start(Gtk.Label(label='Telefones:', xalign=0), False, False, 0)
        self.phone_listbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.pack_start(self.phone_listbox, False, False, 0)

        add_phone_button = Gtk.Button(label="Adicionar Telefone")
        add_phone_button.connect("clicked", self.add_phone)
        box.pack_start(add_phone_button, False, False, 0)

        self.cal = Gtk.Calendar()
        box.pack_start(self.cal, False, False, 0)

        time_hbox = Gtk.Box()
        self.hours_field = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 23, 1, 10, 0))
        self.minutes_field = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 59, 1, 10, 0))
        time_hbox.pack_start(self.hours_field, False, False, 0)
        time_hbox.pack_start(Gtk.Label(label=' : '), False, False, 0)
        time_hbox.pack_start(self.minutes_field, False, False, 0)
        box.pack_start(time_hbox, False, False, 0)

        box.pack_start(Gtk.Label(label='Anotações:', xalign=0), False, False, 0)
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(False)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.set_border_width(2)
        scrolled_window.add(self.textview)
        box.pack_start(scrolled_window, False, False, 0)

        scrolled_box.add(box)
        main_vbox.pack_start(scrolled_box, True, True, 0)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        icon = Gtk.Image.new_from_icon_name("emblem-favorite", Gtk.IconSize.BUTTON)
        button_add_donation = Gtk.Button(label=" Doação")
        button_add_donation.set_image(icon)
        button_add_donation.set_always_show_image(True)
        button_add_donation.connect('clicked', self.on_donation_clicked)
        button_box.pack_start(button_add_donation, False, False, 0)

        self.donation_label = Gtk.Label("R$ 0.00")
        button_box.pack_start(self.donation_label, False, False, 0)
    
        button_set_alarm = Gtk.Button(label="Salvar")
        button_set_alarm.connect('clicked', self.button_set_alarm_clicked)
        button_box.pack_end(button_set_alarm, False, False, 0)
        main_vbox.pack_start(button_box, False, False, 0)

        self.add(main_vbox)
        self.show_all()

    def button_set_alarm_clicked(self, button):
        if not self.v.validate_all():
            print("Campos inválidos")
            return
        try:
            appointment = self.get_appointment_data()
            svc = AppointmentService()
            id = svc.create(self.app.logged_user, appointment)
            print("Compromisso salvo com sucesso!", id)
            self.emit("appointment_saved", id)
            self.destroy()
        except Exception as e:
            print(f"Erro ao salvar compromisso: {e}")

    def get_appointment_data(self):
        year, month, day = self.cal.get_date()
        selected_date = datetime.datetime(year, month + 1, day)
        hours = self.hours_field.get_value_as_int()
        minutes = self.minutes_field.get_value_as_int()
        selected_time = f"{hours:02d}:{minutes:02d}"

        buffer = self.textview.get_buffer()
        start_iter, end_iter = buffer.get_bounds()
        notes = buffer.get_text(start_iter, end_iter, True)

        phone_numbers = [child.get_text().strip() for hbox in self.phone_listbox.get_children()
                        for child in hbox.get_children() if isinstance(child, Gtk.Entry)]
        
        new_call = AppointmentCall(
            donor_id=self.selected_donor.id if self.selected_donor else None,  # Corrigido para evitar None
            phone=",".join(phone_numbers),
            status="Agendado",
        )

        return Appointment(
            date=selected_date,
            time=selected_time,
            event_type='Ligação',
            notes=notes,
            calls=new_call,
            donation=self.new_donation if self.new_donation else None
        )

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

    def delete_phone(self, widget, hbox):
        self.phone_listbox.remove(hbox)
        
    def on_donation_clicked(self, w):
        if not self.selected_donor:
            print("Nenhum doador selecionado!")
            return
        
        appointment = self.get_appointment_data()
        
        appointment.calls.donor = self.selected_donor 

        self.form = DonationNewForm(self.app, self.get_toplevel())
        self.form.from_appointment(appointment)
        self.form.connect("complete_donation", self.on_complete_donation)

    def on_complete_donation(self, w, donation):
        if donation:
            self.new_donation = donation
            print(f"Doação vinculada ao compromisso: {self.new_donation.amount} para {self.new_donation.donor_id}")
            formatted_value = locale.currency(self.new_donation.amount, grouping=True)
            self.donation_label.set_text(f"{formatted_value}")
        else:
            print("Usuário cancelou a doação.")

    def quit_window(self, window):
        self.destroy()

class NewAppointment(AppointmentBase):
    def __init__(self, app, parent):
        super().__init__(app, parent, "Novo Compromisso")

class EditAppointment(AppointmentBase):
    def __init__(self, app, parent, appointment_id):
        super().__init__(app, parent, "Editar Compromisso")
        svc = AppointmentService()
        self.appointment = svc.get_by_id(self.app.logged_user, appointment_id)
        self.load_appointment(self.appointment)

    def load_appointment(self, appointment):
        self.selected_donor = appointment.calls.donor
        self.donor_entry.set_text(self.selected_donor.name)
        
        if appointment.donation:
            formatted_value = locale.currency(appointment.donation.amount, grouping=True)
            self.donation_label.set_text(f"{formatted_value}")

        for phone in appointment.calls.phone.split(","):
            self.add_phone(None, phone)
            
        self.cal.select_month(appointment.date.month - 1, appointment.date.year)
        self.cal.select_day(appointment.date.day)
        self.hours_field.set_value(int(appointment.time.split(':')[0]))
        self.minutes_field.set_value(int(appointment.time.split(':')[1]))
        buffer = self.textview.get_buffer()
        buffer.set_text(appointment.notes)
        

    def button_set_alarm_clicked(self, button):
        if not self.v.validate_all():
            print("Campos inválidos")
            return
        try:
            appointment = self.get_appointment_data()
            appointment.id = self.appointment.id
            svc = AppointmentService()
            svc.update(self.app.logged_user, appointment)
            print("Compromisso atualizado com sucesso!")
            
            appointment = svc.get_by_id(self.app.logged_user, self.appointment.id)
            
            if appointment.donation and appointment.donation.paid:
                # Criar um diálogo perguntando se deseja gerar o recibo
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=Gtk.DialogFlags.MODAL,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text="Recibo",
                )
                dialog.format_secondary_text("Deseja gerar um recibo para esta doação?")
                response = dialog.run()
                dialog.destroy()

                if response == Gtk.ResponseType.YES:
                    print("gerando recibo...")
                    donation_service = DonationService()
                    pdf_path = donation_service.generate_receipt(self.app.logged_user, appointment.donation.id)
                    
                    v = PDFViewer(self.app, self.get_toplevel(), pdf_path)
                
            self.emit("appointment_saved", -1)
            
            self.destroy()
        except Exception as e:
            print(f"Erro ao atualizar compromisso: {e}")
