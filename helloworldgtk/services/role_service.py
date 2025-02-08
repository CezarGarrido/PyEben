from sqlalchemy.orm import Session
from ..models.role import Role
from ..database import Session  # Certifique-se de que o caminho está correto

class RoleService:
    @staticmethod
    def list_roles():
        """
        Retorna uma lista de todas as roles cadastradas no banco de dados.
        :return: Lista de dicionários contendo os dados das roles.
        """
        session = Session()
        try:
            return session.query(Role).all()
        finally:
            session.close()  # Fecha a sessão para evitar vazamentos de conexões
