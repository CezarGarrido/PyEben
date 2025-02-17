from datetime import date
import locale
from sqlalchemy.orm import Session
from ..models.donation import Donation
from ..database import Session
from ..models.user import User
from pathlib import Path
import tempfile
import sys
import os
class DonationService:
    def __init__(self):
        self.db = Session()

    def create(self, user: User, new_donation: Donation):
        """
        Cria um novo usuário na mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param new_user: Objeto User contendo os dados do novo usuário.
        :return: ID do novo usuário criado.
        """
        new_donation.company_id = user.company_id  # Garante que o novo usuário pertença à mesma empresa
        new_donation.user_creator_id = user.id  # Registra o criador do usuário

        self.db.add(new_donation)
        self.db.commit()
        self.db.refresh(new_donation)
        return new_donation.id
    
    def list(self, user: User):
        """
        Lista todos os usuários da mesma empresa do usuário fornecido.
        :param user: Usuário autenticado que está fazendo a requisição.
        :return: Lista de instâncias de User da mesma empresa.
        """
        return self.db.query(Donation).filter(Donation.company_id == user.company_id, Donation.active == True).all()

    def get_by_id(self, user: User, user_id: int):
        """
        Obtém um usuário pelo ID, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param user_id: ID do usuário a ser buscado.
        :return: Instância de User se encontrado e pertencente à mesma empresa, None caso contrário.
        """
        return self.db.query(Donation).filter(Donation.id == user_id, Donation.company_id == user.company_id).first()

    def update(self, user: User, updated_donation: Donation):
        existing = self.get_by_id(user, updated_donation.id)
        if existing:
            self.db.merge(updated_donation)
            self.db.commit()
            return True
        return False

    def deactivate(self, user: User, id: int):
        """
        Desativa um usuário pelo ID, alterando seu status, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param user_id: ID do usuário a ser desativado.
        :return: Booleano indicando se a operação foi bem-sucedida.
        """
        donation = self.get_by_id(user, id)
        if donation:
            donation.active = False
            self.db.commit()
            return True
        return False

    def generate_receipt(self, user, id):
        """
        Converte um arquivo HTML para PDF e salva em um arquivo temporário.
        Retorna o caminho do arquivo temporário.
        """
        # Obtendo a doação do banco de dados
        donation = self.get_by_id(user, id)
        
        if not donation:
            print(f"Erro: Doação com ID {id} não encontrada.")
            return None
        
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        
        # Convertendo o valor da doação para extenso
        valor_formatado = locale.currency(donation.amount, grouping=True, symbol=True)
        contatos = ", ".join([contact.phone for contact in donation.donor.contacts]) if donation.donor and donation.donor.contacts else "Não informado"
        # Mapeando os dados para substituição no template HTML
        donation_data = {
            "NUMERO_RECIBO": str(donation.id),
            "DATA_EMISSAO": date.today().strftime("%d/%m/%Y"),
            "NOME_DOADOR": donation.donor.name if donation.donor else "Desconhecido",
            "CODIGO_DOADOR": str(donation.donor_id),
            "END_RUA_DOADOR": donation.donor.addresses.street if donation.donor else "Não informado",
            "END_NUMERO_DOADOR": str(donation.donor.addresses.number) if donation.donor else "S/N",
            "END_BAIRRO_DOADOR": donation.donor.addresses.neighborhood if donation.donor else "Não informado",
            "CONTATO_DOADOR": contatos,
            "END_CIDADE_DOADOR": donation.donor.addresses.city if donation.donor else "Não informado",
            "END_ESTADO_DOADOR": donation.donor.addresses.state if donation.donor else "Não informado",
            "VALOR_DOADO": f"{donation.amount:.2f}",
            "VALOR_DOADO_EXTENSO": valor_formatado,
        }

        # Caminho do arquivo HTML (template)
        source_html_path = self.get_resource_path("reports/template_recibo.html")
        
        try:
            # Lendo o arquivo HTML
            html_content = Path(source_html_path).read_text(encoding="utf-8")

            # Substituindo os placeholders pelos valores do dicionário
            for chave, valor in donation_data.items():
                html_content = html_content.replace(f"{{{{{chave}}}}}", str(valor))

            # Criando um arquivo temporário para armazenar o PDF
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

            # Convertendo o HTML para PDF e salvando no arquivo temporário

            # Fechando o arquivo temporário para garantir que ele está salvo
            temp_pdf.close()

            # Retornando o caminho do arquivo PDF gerado se não houver erro
            return None

        except Exception as e:
            print(f"Erro ao gerar recibo: {e}")
            return None
        
        
    def get_resource_path(self, relative_path):
        """Retorna o caminho do recurso, lidando com execução via PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            # Quando rodando como executável, os arquivos são extraídos em _MEIPASS
            return os.path.join(sys._MEIPASS, relative_path)
        return relative_path