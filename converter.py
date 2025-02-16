import datetime
import sys

from helloworldgtk.database import Session
from helloworldgtk.models.donor import Donor, DonorAddress, DonorContact
from helloworldgtk.models.employee import Employee, EmployeeAddress, EmployeeContact
from helloworldgtk.models.user import User
sys.path.append("./dataflex_converter")  # Adiciona o diretório ao caminho de busca
import gi
import os
import glob
import dataflex_converter
import csv
import logging
import importlib
import pkgutil
import re
import helloworldgtk.models  # Certifique-se de que este é o caminho correto para os modelos
from helloworldgtk.models.base import Base  # Importa a Base.metadata

# Importa automaticamente todos os módulos dentro de helloworldgtk.models
for _, module_name, _ in pkgutil.iter_modules(helloworldgtk.models.__path__):
    importlib.import_module(f"helloworldgtk.models.{module_name}")
    
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class DataFlexConverterApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Conversor DataFlex para CSV")
        self.set_border_width(10)
        self.set_default_size(400, 250)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Campo de entrada para o diretório de entrada
        self.entry_directory = Gtk.Entry()
        self.entry_directory.set_placeholder_text("Selecione um diretório contendo arquivos .dat")
        btn_directory = Gtk.Button(label="Selecionar")
        btn_directory.connect("clicked", self.on_select_directory)
        
        hbox_directory = Gtk.Box(spacing=5)
        hbox_directory.pack_start(self.entry_directory, True, True, 0)
        hbox_directory.pack_start(btn_directory, False, False, 0)
        vbox.pack_start(hbox_directory, False, False, 0)

        # Campo de entrada para o diretório de saída
        self.entry_output_directory = Gtk.Entry()
        self.entry_output_directory.set_placeholder_text("Selecione um diretório para salvar os arquivos .csv")
        btn_output_directory = Gtk.Button(label="Selecionar")
        btn_output_directory.connect("clicked", self.on_select_output_directory)
        
        hbox_output_directory = Gtk.Box(spacing=5)
        hbox_output_directory.pack_start(self.entry_output_directory, True, True, 0)
        hbox_output_directory.pack_start(btn_output_directory, False, False, 0)
        vbox.pack_start(hbox_output_directory, False, False, 0)

        # Campo de entrada para o separador
        self.entry_separator = Gtk.Entry()
        self.entry_separator.set_placeholder_text("Separador de campos (padrão: |)")
        vbox.pack_start(self.entry_separator, False, False, 0)

        # Botão para converter
        btn_convert = Gtk.Button(label="Converter Todos")
        btn_convert.connect("clicked", self.on_convert)
        vbox.pack_start(btn_convert, False, False, 0)

        self.show_all()

    def on_select_directory(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Selecione um diretório",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        
        if dialog.run() == Gtk.ResponseType.OK:
            self.entry_directory.set_text(dialog.get_filename())
        dialog.destroy()
    
    def on_select_output_directory(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Selecione um diretório de saída",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        
        if dialog.run() == Gtk.ResponseType.OK:
            self.entry_output_directory.set_text(dialog.get_filename())
        dialog.destroy()

    def on_convert(self, widget):
        directory = self.entry_directory.get_text()
        output_directory = self.entry_output_directory.get_text()
        separator = self.entry_separator.get_text() or "|"

        if not directory or not output_directory:
            self.show_message("Erro", "Selecione os diretórios de entrada e saída.")
            return

        dat_files = glob.glob(os.path.join(directory, "*.DAT"))

        if not dat_files:
            self.show_message("Erro", "Nenhum arquivo .dat encontrado no diretório.")
            return

        converted_files = []
        tag_mappings = self.read_tag_files(directory)  # Lê os arquivos .TAG

        try:
            for dat_file in dat_files:
                filename = os.path.splitext(os.path.basename(dat_file))[0]
                output_file = os.path.join(output_directory, filename + ".csv")

                dataflex_converter.convert(dat_file, output_file, separator)

                # Ajustar os nomes das colunas conforme o .TAG
                if filename in tag_mappings:
                    self.clean_and_apply_column_names(output_file, tag_mappings[filename], separator)

                converted_files.append(output_file)

            # Agora processamos cada arquivo gerado
            for csv_file in converted_files:
                self.handle_file(csv_file)

            self.show_message("Sucesso", "Conversão e processamento concluídos com sucesso!")
        except Exception as e:
            self.show_message("Erro", str(e))

    def read_tag_files(self, directory):
        """
        Lê todos os arquivos .TAG no diretório e retorna um dicionário
        com o nome do arquivo base e suas colunas correspondentes.
        """
        tag_files = glob.glob(os.path.join(directory, "*.TAG"))
        tag_mappings = {}

        for tag_file in tag_files:
            filename = os.path.splitext(os.path.basename(tag_file))[0]

            try:
                with open(tag_file, "r", encoding="utf-8") as f:
                    # Filtra apenas linhas válidas e remove caracteres inválidos
                    columns = [
                        line.replace("", "").strip()  # Remove caracteres indesejados
                        for line in f.readlines()
                        if line.strip() and not line.startswith("DATABASE:")
                    ]
                    tag_mappings[filename] = columns

            except Exception as e:
                print(f"Erro ao ler {tag_file}: {e}")

        return tag_mappings

    def clean_and_apply_column_names(self, csv_file, column_names, separator):
        """
        Remove a linha 'DATABASE', caracteres inválidos e renomeia os cabeçalhos do CSV.
        """
        try:
            temp_file = csv_file + ".tmp"

            with open(csv_file, "r", encoding="utf-8") as infile, open(temp_file, "w", encoding="utf-8") as outfile:
                reader = csv.reader(infile, delimiter=separator)
                writer = csv.writer(outfile, delimiter=separator, lineterminator="\n")

                writer.writerow(column_names)  # Garante que o cabeçalho é sempre escrito primeiro

                for row in reader:
                    if "DATABASE:" in row[0]:  # Ignora linhas com DATABASE
                        continue

                    cleaned_row = [col.replace("", "").strip() for col in row]  # Remove caracteres indesejados
                    writer.writerow(cleaned_row)

            os.replace(temp_file, csv_file)  # Substitui o arquivo original pelo novo
        except Exception as e:
            print(f"Erro ao limpar e renomear colunas em {csv_file}: {e}")

    def show_message(self, title, message):
        print(message)
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def handle_file(self, file):
        """ Processa cada arquivo CSV conforme necessário """
        try:
            with open(file, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter= self.entry_separator.get_text() or "|")
                rows = list(reader)

                #if os.path.basename(file) == "JCFUN045.csv":
                    #self.process_jcfun045(rows)
                
                if os.path.basename(file) == "JCDOA005.csv":
                    self.process_donors_csv(rows)
        except Exception as e:
            print(f"Erro ao processar {file}: {e}")
            

    def process_donors_csv(self, rows):
        """
        Processa os dados do CSV de doadores, convertendo para objetos SQLAlchemy
        e inserindo-os no banco de dados.
        """
        session = Session()
        donors = []
        header = [col.strip() for col in rows[0]]

        try:
            for row in rows[1:]:
                try:
                    row_dict = dict(zip(header, row))

                    donor = Donor(
                        id=int(row_dict["COD_DOA"]),
                        name=row_dict["NOM_A"],
                        person_type=row_dict["DES_CLP"],
                        cnpj=row_dict["CGC_DOA"] or None,
                        ie=row_dict["INS_DOA"] or None,
                        cpf=row_dict["CPF_DOA"] or None,
                        rg=row_dict["R_G_DOA"] or None,
                        rg_issuer=row_dict["ORG_EMI"] or None,
                        active=True,
                        user_creator_id=int(row_dict["COD_FUN"]) or 1,
                        company_id=1,  
                    )

                    if row_dict["TEL_DOA"]:
                        contact = DonorContact(
                            donor=donor,
                            name=row_dict["NOM_B"] or row_dict["NOM_A"],
                            phone=row_dict["TEL_DOA"]
                        )
                        donor.contacts.append(contact)

                    if row_dict["END_DOA"] and row_dict["CID_DOA"]:
                        address = DonorAddress(
                            donor=donor,
                            street=row_dict["END_DOA"],
                            neighborhood=row_dict["BAI_DOA"] or None,
                            complement=row_dict["COM_END"] or None,
                            city=row_dict["CID_DOA"],
                            state=row_dict["EST_DOA"][:2] if row_dict["EST_DOA"] else "?",
                            postal_code=row_dict["CEP_DOA"] or None,
                            number="S/N"
                        )
                        donor.addresses = address

                    session.add(donor)
                    session.flush()

                    donors.append(donor)

                except KeyError as e:
                    logging.error(f"Erro ao processar linha {row}: Campo ausente - {e}")
                except ValueError as e:
                    logging.error(f"Erro ao converter valores da linha {row}: {e}")
                except Exception as e:
                    logging.error(f"Erro inesperado ao processar linha {row}: {e}")

            if donors:
                session.commit()
                logging.info(f"{len(donors)} doadores inseridos com sucesso.")
            else:
                logging.warning("Nenhum doador válido para inserção.")

        except Exception as e:
            session.rollback()
            logging.critical(f"Erro ao inserir dados no banco: {e}")
        finally:
            session.close()

    def process_jcfun045(self, rows):
        """
        Processa os dados do arquivo JCFUN045.csv, convertendo para objetos SQLAlchemy
        e inserindo-os no banco de dados.
        """
        session = Session()
        employees = []

        header = [col.strip() for col in rows[0]]

        try:
            for row in rows[1:]:
                try:
                    row_dict = dict(zip(header, row))

                    if not row_dict["NAS_FUN"].replace("/", "").isdigit():
                        row_dict["NAS_FUN"] = None

                    rg_number, rg_issuer = clean_rg(row_dict["RG_FUN"])

                    employee = Employee(
                        id=int(row_dict["COD_FUN"]),
                        name=row_dict["NOM_FUN"],
                        date_of_birth=parse_date(row_dict["NAS_FUN"]),
                        hire_date=parse_date(row_dict["DAT_ADM"]),
                        termination_date=parse_date(row_dict["DAT_DEM"]),
                        ctps=row_dict["CTPS"] or None,
                        cpf=clean_cpf(row_dict["CPF_FUN"]),
                        rg=rg_number,
                        rg_issuer=rg_issuer,
                        department=row_dict["DES_SET"] or None,
                        position=row_dict["DES_SET"] or None,
                        salary=float(row_dict["SAL_FUN"]) if row_dict["SAL_FUN"] else None,
                        marital_status=row_dict["EST_CIV"] or None,
                        wife_name=row_dict["NOM_CON"] or None,
                        wife_date_of_birth=parse_date(row_dict["NAS_CON"]),
                        active=True,  
                        company_id=1,  
                        user_creator_id=1,  
                    )
                    
                    if row_dict["TEL_RES"]:
                        contact = EmployeeContact(
                            employee=employee,
                            name=row_dict["NOM_FUN"],
                            phone=row_dict["TEL_RES"]
                        )
                        employee.contacts.append(contact)

                    if row_dict["END_FUN"] and row_dict["CID_FUN"]:
                        address = EmployeeAddress(
                            employee=employee,
                            street=row_dict["END_FUN"],
                            neighborhood=row_dict["BAI_FUN"] or None,
                            postal_code=row_dict["CEP_FUN"] or None,
                            city=row_dict["CID_FUN"],
                            state=row_dict["EST_FUN"],
                            number="S/N"
                        )
                        employee.addresses = address

                    session.add(employee)
                    session.flush()

                    username = clean_cpf(row_dict["CPF_FUN"])
                    user = User(
                        company_id=employee.company_id,
                        employee_id=employee.id, 
                        username=username,
                        email=username + "@empresa.com",
                        active=True,
                        role_id=2,  # 🔹 Definir um role_id padrão
                        user_creator_id=1,  
                    )
                    
                    user.set_password(row_dict["SEN_ACE"])

                    session.add(user)

                    employees.append(employee)

                except KeyError as e:
                    logging.error(f"Erro ao processar linha {row}: Campo ausente - {e}")
                except ValueError as e:
                    logging.error(f"Erro ao converter valores da linha {row}: {e}")
                except Exception as e:
                    logging.error(f"Erro inesperado ao processar linha {row}: {e}")

            if employees:
                session.commit()
                logging.info(f"{len(employees)} funcionários inseridos com sucesso.")
            else:
                logging.warning("Nenhum funcionário válido para inserção.")

        except Exception as e:
            session.rollback()
            logging.critical(f"Erro ao inserir dados no banco: {e}")
        finally:
            session.close()

def clean_rg(rg):
    """ 
    Remove espaços extras e separa o RG do órgão emissor.
    Retorna os primeiros 11 caracteres para `rg` e o restante para `rg_issuer`.
    """
    if not rg:
        return None, None

    parts = rg.split()
    rg_number = parts[0][:11]  # Apenas o número (limita a 11 caracteres)
    rg_issuer = " ".join(parts[1:]) if len(parts) > 1 else None  # O que sobra é o órgão emissor

    return rg_number, rg_issuer

def clean_cpf(cpf):
    """ Remove pontos e traços do CPF, garantindo que tenha no máximo 11 caracteres """
    return re.sub(r"\D", "", cpf)[:11] if cpf else None

def parse_date(date_str):
    """Converte strings de data do formato 'DD/MM/YYYY' para objetos datetime."""
    if not date_str or date_str.strip() in ["", "01/01/1000"]:
        return None  # Se for nulo ou '01/01/1000', retorna None
    
    try:
        # Verifica se a string contém exatamente 10 caracteres no formato esperado
        if len(date_str.strip()) == 10 and date_str.count("/") == 2:
            return datetime.datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
        else:
            logging.warning(f"Valor ignorado como data inválida: {date_str}")
            return None
    except ValueError:
        logging.warning(f"Erro ao converter data: {date_str}")
        return None
    
def parse_salary(salary_str):
     """Converte salários para float."""
     try:
         return float(salary_str)
     except ValueError:
         return None  # Se houver erro, assume que o salário é nulo


if __name__ == "__main__":
    app = DataFlexConverterApp()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()
