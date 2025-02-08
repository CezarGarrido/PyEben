import datetime
import gi
import locale
import re

from helloworldgtk.models.donor import Donor, DonorAddress, DonorContact
from helloworldgtk.services.donor_service import DonorService
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from ...widget.validate_entry import FormValidator
from ...services.postal_code_service import Address

# Definir a localização para exibir os valores corretamente em BRL
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

class EditForm(Gtk.Window):
    __gsignals__ = {
        "donor_updated": (GObject.SignalFlags.RUN_FIRST, None, (int,)),  # Agora aceita um argumento tipo str
    }
        
    def __init__(self, app, parent, donor_id):
        super().__init__(title="Editar Doador")

        self.set_default_size(450, 350)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.app = app
        self.donor_id = donor_id
        self.v = FormValidator()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.add(vbox)

        # Criando Notebook (Abas)
        notebook = Gtk.Notebook()
        vbox.pack_start(notebook, True, True, 0)

        notebook.append_page(self.create_personal_tab(), Gtk.Label(label="Dados Pessoais"))
        notebook.append_page(self.create_address_tab(), Gtk.Label(label="Endereço"))
        notebook.append_page(self.create_contact_tab(), Gtk.Label(label="Contato"))

        # Botão de salvar
        button = Gtk.Button(label="Salvar")
        button.connect("clicked", self.on_save_clicked)
        vbox.pack_start(button, False, False, 0)
        self.load_donor_data()
        self.show_all()

    def load_donor_data(self):
        svc = DonorService()
        donor = svc.get_by_id(self.app.logged_user, self.donor_id)

        if not donor:
            self.show_error("Doador não encontrado.")
            self.destroy()
            return

        self.name_entry.set_text(donor.name)
       
        if donor.person_type != "Pessoa Física":
            self.person_type_combo.set_active(1)  # Define "Pessoa Física" como padrão

        self.cpf_entry.set_text(donor.cpf)
        self.cnpj_entry.set_text(donor.cnpj)
        self.rg_entry.set_text(donor.rg)
        self.rg_issuer_entry.set_text(donor.rg_issuer)

        if donor.addresses:
            self.postal_code_entry.set_text(donor.addresses.postal_code)
            self.city_entry.set_text(donor.addresses.city)
            self.state_entry.set_text(donor.addresses.state)
            self.street_entry.set_text(donor.addresses.street)
            self.number_entry.set_text(donor.addresses.number)
            self.neighborhood_entry.set_text(donor.addresses.neighborhood)
            self.complement_entry.set_text(donor.addresses.complement)

        self.contacts_store.clear()
        for contact in donor.contacts:
            self.contacts_store.append([contact.name, contact.phone, contact.email])

    def create_personal_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)
        
        # Combobox para seleção de tipo de pessoa
        self.person_type_combo = Gtk.ComboBoxText()
        self.person_type_combo.append_text("Pessoa Física")
        self.person_type_combo.append_text("Pessoa Jurídica")
        self.person_type_combo.set_active(0)  # Define "Pessoa Física" como padrão
        self.person_type_combo.connect("changed", self.on_person_type_changed)

        self.calendar_label = Gtk.Label(label="Data de Nascimento:", xalign=0)

        # Campos
        self.name_entry = self.v.add("Nome:", validate_name)
        self.cpf_entry = self.v.add("CPF:", validate_cpf, format_cpf)
        self.cnpj_entry = self.v.add("CNPJ:")
        self.ie_entry = self.v.add("Inscrição Estadual:")

        # RG e Órgão Emissor
        self.rg_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.rg_entry = self.v.add("RG:")
        self.rg_issuer_entry = self.v.add("Órgão Emissor:")
        self.rg_box.pack_start(self.rg_entry, True, True, 0)
        self.rg_box.pack_start(self.rg_issuer_entry, True, True, 0)


        # Adiciona widgets ao layout
        box.pack_start(Gtk.Label(label="Tipo de Pessoa:", xalign=0), False, False, 0)
        box.pack_start(self.person_type_combo, False, False, 0)
        box.pack_start(self.name_entry, False, False, 0)
        box.pack_start(self.cpf_entry, False, False, 0)
        box.pack_start(self.rg_box, False, False, 0)
        box.pack_start(self.cnpj_entry, False, False, 0)
        box.pack_start(self.ie_entry, False, False, 0)
        self.update_fields_visibility()

        return box
    
    def on_person_type_changed(self, combo):
        self.update_fields_visibility()

    def update_fields_visibility(self):
        is_fisica = self.person_type_combo.get_active() == 0
        
        print("is fisica {}", is_fisica)
        self.cpf_entry.set_visible(is_fisica)
        self.rg_box.set_visible(is_fisica)

        self.cnpj_entry.set_visible(not is_fisica)
        self.ie_entry.set_visible(not is_fisica)

    def on_key_press(self, widget, event):
        """Detecta teclas pressionadas no Gtk.Calendar."""
        if event.keyval == Gdk.KEY_Return:
            # Seleciona a data onde o cursor está
            self.on_date_selected(widget)

    def on_calendar_icon_clicked(self, button):
        # Exibe o popover com o calendário ao clicar no ícone
        self.calendar_popover.set_relative_to(button)
        self.calendar_popover.show_all()

    def on_date_selected(self, calendar):
        # Obtém a data selecionada
        year, month, day = calendar.get_date()
        formatted_date = f"{day:02d}/{month + 1:02d}/{year}"  # Formata a data (mês começa em 0)
        self.birth_date_entry.set_text(formatted_date)
        self.calendar_popover.popdown()  # Fecha o popover

    def create_address_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)

        cep_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        self.postal_code_label = Gtk.Label(label="CEP:", xalign=0)
        self.postal_code_entry = Gtk.Entry()
        self.postal_code_button = Gtk.Button.new_from_icon_name("system-search-symbolic", Gtk.IconSize.BUTTON)
        self.postal_code_button.connect("clicked", self.on_search_cep)

        cep_box.pack_start(self.postal_code_entry, False, False, 0)
        cep_box.pack_start(self.postal_code_button, False, False, 0)

        self.city_entry = self.v.add("Cidade:")
        self.state_entry = self.v.add("Estado:")
        self.street_entry = self.v.add("Rua:")
        self.number_entry = self.v.add("Número:")
        self.neighborhood_entry = self.v.add("Bairro:")
        self.complement_entry = self.v.add("Complemento:")


        box.pack_start(self.postal_code_label, False, False, 0)
        box.pack_start(cep_box, False, False, 0)

        box.pack_start(self.street_entry, False, False, 0)
        box.pack_start(self.city_entry, False, False, 0)
        box.pack_start(self.state_entry, False, False, 0)
        box.pack_start(self.number_entry, False, False, 0)
        box.pack_start(self.neighborhood_entry, False, False, 0)
        box.pack_start(self.complement_entry, False, False, 0)

        return box
    
    def create_contact_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)
        
        # Lista de contatos
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.contacts_store = Gtk.ListStore(str, str, str)
        self.contacts_view = Gtk.TreeView(model=self.contacts_store)
        self.contacts_view.set_rules_hint(True)  # Habilita "zebra" na lista
        
        for i, column_title in enumerate(["Nome", "Telefone", "E-mail"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_resizable(True)
            self.contacts_view.append_column(column)
            
        self.contacts_view.get_style_context().add_class("view")
        
        hbox.pack_start(self.contacts_view, True, True, 0)

        # Botões de ação
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=5)
        add_button = Gtk.Button(label="Adicionar")
        add_button.connect("clicked", self.on_add_contact)
        button_box.pack_start(add_button, False, False, 0)

        remove_button = Gtk.Button(label="Remover")
        remove_button.connect("clicked", self.on_remove_contact)
        button_box.pack_start(remove_button, False, False, 0)

        edit_button = Gtk.Button(label="Editar")
        edit_button.connect("clicked", self.on_edit_contact)
        button_box.pack_start(edit_button, False, False, 0)

        hbox.pack_start(button_box, False, False, 0)
        vbox.pack_start(hbox, True, True, 0)

        return vbox

    def open_contact_dialog(self, title, contact=None):
        dialog = Gtk.Dialog(title, self, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_default_size(250, 150)

        box = dialog.get_content_area()
        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=5)

        entry_name = Gtk.Entry()
        entry_phone = Gtk.Entry()
        entry_email = Gtk.Entry()

        form_box.pack_start(Gtk.Label(label="Nome:"), False, False, 0)
        form_box.pack_start(entry_name, False, False, 0)
        form_box.pack_start(Gtk.Label(label="Telefone:"), False, False, 0)
        form_box.pack_start(entry_phone, False, False, 0)
        form_box.pack_start(Gtk.Label(label="E-mail:"), False, False, 0)
        form_box.pack_start(entry_email, False, False, 0)
        
        if contact:
            entry_name.set_text(contact[0])
            entry_phone.set_text(contact[1])
            entry_email.set_text(contact[2])

        box.add(form_box)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_contact = (entry_name.get_text(), entry_phone.get_text(), entry_email.get_text())
            dialog.destroy()
            return new_contact
        else:
            dialog.destroy()
            return None

    def on_add_contact(self, widget):
        new_contact = self.open_contact_dialog("Adicionar Contato")
        if new_contact:
            self.contacts_store.append(list(new_contact))

    def on_remove_contact(self, widget):
        selection = self.contacts_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            model.remove(treeiter)

    def on_edit_contact(self, widget):
        selection = self.contacts_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            contact = list(model[treeiter])
            updated_contact = self.open_contact_dialog("Editar Contato", contact)
            if updated_contact:
                model[treeiter] = updated_contact

    def create_contact_tab1(self):
        list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)


        frame1 = Gtk.Frame(label="Nome")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10) 
        self.contact_name_entry = self.v.add("Nome:")
        self.contact_phone_entry = self.v.add("Telefone:")
        self.contact_email_entry = self.v.add("E-mail:")
        
        box.pack_start(self.contact_name_entry, False, False, 0)
        box.pack_start(self.contact_phone_entry, False, False, 0)
        box.pack_start(self.contact_email_entry, False, False, 0)
        frame1.add(box)

        list.pack_start(frame1, False, False, 0)

        return list

    def on_save_clicked(self, widget):
        if not self.v.validate_all():
            print("inválidos")
            return
        
        svc = DonorService()
        donor = svc.get_by_id(self.app.logged_user, self.donor_id)
        
        if not donor:
            self.show_error("Funcionário não encontrado.")
            return
        
        # Capturando os dados do formulário
        name = self.name_entry.get_text()
        cpf = self.cpf_entry.get_text().replace(".", "").replace("-", "")  # Remove formatação
        cnpj = self.cnpj_entry.get_text().replace(".", "").replace("-", "")  # Remove formatação
        rg = self.rg_entry.get_text()
        rg_issuer = self.rg_issuer_entry.get_text()
        ie = self.ie_entry.get_text()
        person_type = self.person_type_combo.get_active_text()
        # Convertendo datas

        donor.name = name
        donor.person_type = person_type

        if person_type == "Pessoa Física":
            donor.cpf = cpf
            donor.rg=rg,
            donor.rg_issuer=rg_issuer
        else:
            donor.cnpj=cnpj
            donor.ie=ie


        donor.addresses.street = self.street_entry.get_text()
        donor.addresses.neighborhood = self.neighborhood_entry.get_text()
        donor.addresses.complement = self.complement_entry.get_text()
        donor.addresses.city = self.city_entry.get_text()
        donor.addresses.state = self.state_entry.get_text()
        donor.addresses.postal_code = self.postal_code_entry.get_text()
        donor.addresses.number = self.number_entry.get_text()
        
        contacts = []
        for row in self.contacts_store:
            contacts.append(DonorContact(name=row[0], phone=row[1], email=row[2]))
        donor.contacts = contacts

        try:
            # Salvando no banco de dados
            service = DonorService()
            id = service.update(self.app.logged_user, donor)
            
            print(f"donor_added ID: {id}")
            self.emit("donor_updated", id)  

            # Fechar a janela após salvar
            self.destroy()

        except ValueError as e:
            self.show_error(f"Erro ao salvar empregado: {e}")
        except Exception as e:
            self.show_error(f"Erro ao salvar empregado: {e}")

    
    def on_search_cep(self, button):
        cep = self.postal_code_entry.get_text().strip()
        address = Address.fetch(cep)

        self.city_entry.set_text(address.city)
        self.state_entry.set_text(address.state)
        self.street_entry.set_text(address.street)
        self.number_entry.set_text(address.number)
        self.neighborhood_entry.set_text(address.neighborhood)
        self.complement_entry.set_text(address.complement)

    def show_error(self, message):
        """Exibe um diálogo de erro."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Erro",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

def validate_name(value):
    value = value.strip()
    if len(value) == 0:
        return "Campo Obrigatório"
    
    return "Nome deve ter pelo menos 2 caracteres" if len(value) < 2 else None

def validate_cpf(value):
    value = value.strip()
    if len(value) == 0:
        return "Campo Obrigatório"
    
    return "CPF inválido (deve ter 11 números)" if not re.match(r"^\d{11}$", value) else None

def format_cpf(cpf):
    if len(cpf) > 11:
        cpf = cpf[:11]  # Limita a 11 dígitos
    
    formatted = "".join(cpf)
    if len(cpf) > 9:
        formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    elif len(cpf) > 6:
        formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
    elif len(cpf) > 3:
        formatted = f"{cpf[:3]}.{cpf[3:]}"
    
    return formatted
