import locale
import gi
from helloworldgtk.models.appointment import Appointment, AppointmentCall
from helloworldgtk.services.appointment_service import AppointmentService
from helloworldgtk.views.donor.search import DonorSearchDialog
from helloworldgtk.widget.validate_entry import FormValidator
from helloworldgtk.views.donation.new import NewForm as DonationNewForm
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GObject, Gdk
import datetime

class NewAppointment(Gtk.Window):
    __gsignals__ = {
        "appointment_added": (GObject.SignalFlags.RUN_FIRST, None, (int,)),  # Agora aceita um argumento tipo str
    }

    def __init__(self, app, parent):
        Gtk.Window.__init__(self, title="Novo Compromisso")
        self.set_default_size(350, 580)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_vexpand(False)

        self.app = app
        self.new_donation = None
        self.connect('destroy', self.quit_window)
        self.v = FormValidator()
        # Contêiner principal
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_vbox.set_border_width(10)

        # Scrolled box para os campos do formulário
        scrolled_box = Gtk.ScrolledWindow()
        scrolled_box.set_hexpand(True)
        scrolled_box.set_vexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Descrição
        #box.pack_start(Gtk.Label(label='Descrição:', xalign=0), False, False, 0)
        #self.task_field = Gtk.Entry()
        #box.pack_start(self.task_field, False, False, 0)

        # Doador        
        self.donor_entry = self.v.add("Doador:")
        self.donor_entry.entry.set_editable(False)
        self.donor_entry.entry.connect("button-press-event", self.on_donor_entry_clicked)
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
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)  # Quebra de linha automática

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(False)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)  # Adiciona uma borda semelhante ao Gtk.Entry
        scrolled_window.set_border_width(2)  # Define um espaçamento mínimo ao redor

        # Adiciona a TextView na ScrolledWindow
        scrolled_window.add(self.textview)

        box.pack_start(scrolled_window, False, False, 0)

        # Adiciona a caixa de rolagem ao contêiner principal
        scrolled_box.add(box)
        main_vbox.pack_start(scrolled_box, True, True, 0)

        self.apply_css()
        
        # Criar um contêiner horizontal para os botões
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Criar o botão de Doação e alinhá-lo à esquerda
        # Criar a imagem do ícone (usando um ícone embutido do GTK)
        icon = Gtk.Image.new_from_icon_name("emblem-favorite", Gtk.IconSize.BUTTON)  # Ícone de doação

        # Criar o botão de Doação e alinhá-lo à esquerda
        button_add_donation = Gtk.Button(label=" Doação")
        button_add_donation.set_image(icon)  # Adiciona o ícone ao botão
        button_add_donation.set_always_show_image(True)  # Garante que o ícone seja mostrado
        button_add_donation.connect('clicked', self.on_donation_clicked)
        button_box.pack_start(button_add_donation, False, False, 0)  # Alinhado à esquerda

        self.donation_label = Gtk.Label("R$ 0.00")
        button_box.pack_start(self.donation_label, False, False, 0)  # Alinhado à esquerda

        # Criar o botão Salvar e alinhá-lo à direita
        button_set_alarm = Gtk.Button(label="Salvar")
        button_set_alarm.connect('clicked', self.button_set_alarm_clicked)
        button_box.pack_end(button_set_alarm, False, False, 0)  # Alinhado à direita


        # Adiciona a caixa de botões ao layout principal
        main_vbox.pack_start(button_box, False, False, 0)

        # Adiciona tudo à janela
        self.add(main_vbox)

        self.show_all()

    def on_donation_clicked(self, w):
        if not hasattr(self, 'selected_donor') or not self.selected_donor:
            print("Nenhum doador selecionado!")
            return
        
        appointment = self.new_appointment()
        appointment.calls.donor = self.selected_donor

        self.form = DonationNewForm(self.app, self.get_toplevel())
        self.form.from_appointment(appointment)  # Passa os dados do compromisso para a doação
        self.form.connect("complete_donation", self.on_complete_donation)

        
    def on_complete_donation(self, w, donation):
        if donation:  # Captura a doação gerada pelo formulário
            self.new_donation = donation
            print(f"Doação vinculada ao compromisso: {self.new_donation.amount} para {self.new_donation.donor_id}")
            formatted_value = locale.currency(self.new_donation.amount, grouping=True)
            self.donation_label.set_text(f"{formatted_value}")
        else:
            print("Usuário cancelou a doação.")

    def apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            button.green-button {
                background: green;
                color: white;
            }
        """)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

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
        if not self.v.validate_all():
            print("inválidos")
            return
        # Capturar dados do formulário
        donor = self.selected_donor
        if not donor:
            print("Erro: Nenhum doador selecionado.")
            return
       # Salvar no banco de dados
    
        try:
            appointment = self.new_appointment()
            appointment.calls.donor_id = donor.id
            
            if self.new_donation:
                appointment.donation = self.new_donation

            svc = AppointmentService()
            id = svc.create(self.app.logged_user, appointment)
            print("Compromisso salvo com sucesso! {}", id)
            self.emit("appointment_added", id)
            self.destroy()
        except Exception as e:
            print(f"Erro ao salvar compromisso: {e}")


    def new_appointment(self):
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
        new_appointment = Appointment(
            date=selected_date,
            time=selected_time,
            event_type='Ligação',
            notes=notes,
        )
        # Capturar a lista de telefones
        phone_numbers = []
        for hbox in self.phone_listbox.get_children():
            for child in hbox.get_children():
                if isinstance(child, Gtk.Entry):
                    phone_numbers.append(child.get_text().strip())
        phone_numbers_str = ",".join(phone_numbers)  # Converte a lista para string separada por vírgulas
        # Adicionar chamadas telefônicas associadas
        new_call = AppointmentCall(
            phone=phone_numbers_str,
            status="Agendado"
        )

        new_appointment.calls = new_call
        return new_appointment
        
    def valid_donor(self, value):
        print("Doador {}", value)
        value = value.strip()
        if len(value) == 0:
            return "Campo Obrigatório"
        return None