import datetime
import gi
import locale
import re

from helloworldgtk.models.donation import Donation
from helloworldgtk.views.donor.search import DonorSearchDialog

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from ...widget.validate_entry import FormValidator
from ...services.donation_service import DonationService

# Definir a localização para exibir os valores corretamente em BRL
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class BaseDonationForm(Gtk.Window):
    def __init__(self, app, parent, title):
        super().__init__(title=title)

        self.set_default_size(300, 250)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.app = app
        self.v = FormValidator()

        self.selected_donor = None
        self.donation = None
        self.is_appointment = False
        self.init_ui()

    def init_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.add(vbox)

        self.donor_entry = self.v.add("Doador:")
        self.donor_entry.entry.set_editable(False)
        self.donor_entry.entry.connect("button-press-event", self.on_donor_entry_clicked)

        self.amount_entry = self.v.add("Valor:", validate_amount, format_amount)

        self.paid_switch = Gtk.Switch()
        self.paid_switch.set_active(False)
        self.paid_switch.connect("state-set", self.on_paid_toggled)
        paid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        paid_box.pack_start(Gtk.Label(label="Pago"), False, False, 0)
        paid_box.pack_start(self.paid_switch, False, False, 0)

        self.received_at_entry = Gtk.Entry()
        self.received_at_entry.set_editable(False)

        calendar_icon = Gtk.Button.new_from_icon_name("x-office-calendar-symbolic", Gtk.IconSize.BUTTON)
        calendar_icon.connect("clicked", self.on_calendar_icon_clicked)

        calendar_label = Gtk.Label(label="Data de Recebimento:", xalign=0)

        self.date_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        calendar_entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        calendar_entry_box.pack_start(self.received_at_entry, True, True, 0)
        calendar_entry_box.pack_start(calendar_icon, False, False, 0)
        self.date_box.pack_start(calendar_label, True, True, 0)
        self.date_box.pack_start(calendar_entry_box, True, True, 0)

        self.date_box.set_sensitive(False)

        self.calendar_popover = Gtk.Popover()
        self.calendar = Gtk.Calendar()
        self.calendar.connect("day-selected-double-click", self.on_date_selected)
        self.calendar.connect("key-press-event", self.on_key_press)
        self.calendar_popover.add(self.calendar)
        self.calendar_popover.set_position(Gtk.PositionType.BOTTOM)

        self.notes_entry = self.v.add("Notas:")

        vbox.pack_start(self.donor_entry, False, False, 0)
        vbox.pack_start(self.amount_entry, False, False, 0)
        vbox.pack_start(paid_box, False, False, 0)
        vbox.pack_start(self.date_box, False, False, 0)
        vbox.pack_start(self.notes_entry, False, False, 0)

        button = Gtk.Button(label="Salvar")
        button.connect("clicked", self.on_save_clicked)
        vbox.pack_start(button, False, False, 0)

    def on_donor_entry_clicked(self, widget, event):
        dialog = DonorSearchDialog(self, self.app.logged_user)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.selected_donor = dialog.get_selected_donor()
            if self.selected_donor:
                self.donor_entry.set_text(self.selected_donor.name)
        dialog.destroy()


    def on_paid_toggled(self, switch, state):
        """Habilita ou desabilita a edição da data e preenche automaticamente a data de recebimento se pago."""
        self.date_box.set_sensitive(state)

        if state:
            today = datetime.date.today().strftime("%d/%m/%Y")
            self.received_at_entry.set_text(today)
        else:
            self.received_at_entry.set_text("")

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.on_date_selected(widget)

    def on_calendar_icon_clicked(self, button):
        self.calendar_popover.set_relative_to(button)
        self.calendar_popover.show_all()

    def on_date_selected(self, calendar):
        year, month, day = calendar.get_date()
        formatted_date = f"{day:02d}/{month + 1:02d}/{year}"
        self.received_at_entry.set_text(formatted_date)
        self.calendar_popover.popdown()

    def on_save_clicked(self, widget):
        raise NotImplementedError("Subclasses devem implementar este método.")


class NewForm(BaseDonationForm):
    __gsignals__ = {
        "donation_saved": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
        "complete_donation": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, app, parent):
        super().__init__(app, parent, "Nova Doação")
        self.show_all()

    def on_save_clicked(self, widget):
        if not self.v.validate_all():
            print("Dados inválidos")
            return

        amount = float(self.amount_entry.get_text().replace("R$", "").replace(".", "").replace(",", "."))
        paid = self.paid_switch.get_active()
        received_at = datetime.datetime.strptime(self.received_at_entry.get_text(), "%d/%m/%Y").date() if paid else None
        received_time = datetime.datetime.now().strftime("%H:%M:%S") if paid else None
        notes = self.notes_entry.get_text()

        self.donation = Donation(
            donor_id=self.selected_donor.id,
            amount=amount,
            notes=notes,
            paid=paid,
            received_at=received_at,
            received_time=received_time,
        )
        
        if self.is_appointment:
            print("Doação criada dentro do compromisso, retornando sem salvar no banco.")
            self.emit("complete_donation", self.donation)

            self.destroy()  # Fecha o formulário
            return  # Apenas retorna, sem salvar no banco

        try:
            donation_service = DonationService()
            donation_id = donation_service.create(self.app.logged_user, self.donation)
            print(f"Doação salva com ID: {donation_id}")
            self.emit("donation_saved", donation_id)
            self.destroy()
        except Exception as e:
            self.show_error(f"Erro ao salvar doação: {e}")

    def from_appointment(self, appointment):
        """
        Ativa o modo de compromisso e cria uma doação sem salvar no banco.
        """
        self.is_appointment = True
        self.selected_donor = appointment.calls.donor
        self.donor_entry.set_text(self.selected_donor.name)
        self.donor_entry.entry.set_sensitive(False)  # Bloqueia edição do doador
        
class EditForm(BaseDonationForm):
    __gsignals__ = {
        "donation_updated": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    def __init__(self, app, parent, id):
        super().__init__(app, parent, "Editar Doação")
        self.donation_id = id
        self.load_donation_data()
        self.show_all()

    def load_donation_data(self):
        svc = DonationService()
        self.donation = svc.get_by_id(self.app.logged_user, self.donation_id)

        self.donor_entry.set_text(self.donation.donor.name)
        self.amount_entry.set_text(str(self.donation.amount))
        self.paid_switch.set_active(self.donation.paid)
        self.received_at_entry.set_text(self.donation.received_at.strftime("%d/%m/%Y") if self.donation.received_at else "")
        self.notes_entry.set_text(self.donation.notes or "")

        self.selected_donor = self.donation.donor

    def on_save_clicked(self, widget):
        if not self.v.validate_all():
            print("Dados inválidos")
            return

        amount = float(self.amount_entry.get_text().replace("R$", "").replace(".", "").replace(",", "."))
        paid = self.paid_switch.get_active()
        received_at = datetime.datetime.strptime(self.received_at_entry.get_text(), "%d/%m/%Y").date() if paid else None
        received_time = datetime.datetime.now().strftime("%H:%M:%S") if paid else None
        notes = self.notes_entry.get_text()

        self.donation.amount = amount
        self.donation.notes = notes
        self.donation.paid = paid
        self.donation.received_at = received_at
        self.donation.received_time = received_time

        try:
            donation_service = DonationService()
            donation_id = donation_service.update(self.app.logged_user, self.donation)
            print(f"Doação atualizada com ID: {donation_id}")
            self.emit("donation_updated", donation_id)
            self.destroy()
        except Exception as e:
            self.show_error(f"Erro ao atualizar doação: {e}")


def validate_amount(value):
    value = value.strip()
    if len(value) == 0:
        return "Campo obrigatório"
    try:
        return "Valor deve ser positivo" if float(value) <= 0 else None
    except ValueError:
        return "Insira um número válido"

def format_amount(value):
    try:
        return locale.currency(float(value), grouping=True) if value else ""
    except ValueError:
        return ""

def validate_date(value):
    value = value.strip()
    if len(value) == 0:
        return None
    try:
        datetime.datetime.strptime(value, "%d/%m/%Y")
        return None
    except ValueError:
        return "Data inválida (use DD/MM/AAAA)"

def format_date(value):
    return value if re.match(r"^\d{2}/\d{2}/\d{4}$", value) else ""
