from sqlalchemy import String, cast, desc, func, or_
from sqlalchemy.orm import Session
from ..models.donor import Donor, DonorContact
from ..database import Session
from ..models.user import User

class DonorService:
    def __init__(self):
        self.db = Session()

    def create(self, user: User, new_donor: Donor):
        """
        Cria um novo usuário na mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param new_user: Objeto User contendo os dados do novo usuário.
        :return: ID do novo usuário criado.
        """
        new_donor.company_id = user.company_id  # Garante que o novo usuário pertença à mesma empresa
        new_donor.user_creator_id = user.id  # Registra o criador do usuário

        self.db.add(new_donor)
        self.db.commit()
        self.db.refresh(new_donor)
        return new_donor.id
    
    def list(self, user: User):
        """
        Lista todos os usuários da mesma empresa do usuário fornecido.
        :param user: Usuário autenticado que está fazendo a requisição.
        :return: Lista de instâncias de User da mesma empresa.
        """
        return self.db.query(Donor).filter(Donor.company_id == user.company_id).order_by(desc(Donor.id)).all()

    def get_by_id(self, user: User, user_id: int):
        """
        Obtém um usuário pelo ID, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param user_id: ID do usuário a ser buscado.
        :return: Instância de User se encontrado e pertencente à mesma empresa, None caso contrário.
        """
        return self.db.query(Donor).filter(Donor.id == user_id, Donor.company_id == user.company_id).first()

    def update(self, user: User, updated_donor: Donor):
        existing = self.get_by_id(user, updated_donor.id)
        if existing:
            self.db.query(DonorContact).filter_by(donor_id=updated_donor.id).delete()
            self.db.merge(updated_donor)
            self.db.commit()
            return True
        return False

    def deactivate(self, user: User, user_id: int):
        """
        Desativa um usuário pelo ID, alterando seu status, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param user_id: ID do usuário a ser desativado.
        :return: Booleano indicando se a operação foi bem-sucedida.
        """
        user_to_deactivate = self.get_by_id(user, user_id)
        if user_to_deactivate:
            user_to_deactivate.active = False
            self.db.commit()
            return True
        return False

    def search(self, user: User, search_term: str, offset=0, limit=10):
        """
        Busca doadores da mesma empresa, permitindo pesquisa por nome e ID,
        mesmo quando search_term contém números e texto misturados.
        """
        query = self.db.query(Donor).filter(Donor.company_id == user.company_id)

        if search_term:
            query = query.filter(or_(
                Donor.name.ilike(f"%{search_term}%"),
                cast(Donor.id, String).ilike(f"%{search_term}%")  # Converte ID para texto
            ))

        return query.order_by(desc(Donor.id)).offset(offset).limit(limit).all()
    
    def count(self, user: User, search_term: str = ""):
        """
        Retorna o número total de doadores que pertencem à empresa do usuário.
        Se um termo de busca for fornecido, conta apenas os doadores correspondentes.
        """
        query = self.db.query(func.count(Donor.id)).filter(Donor.company_id == user.company_id)

        if search_term:
            query = query.filter(or_(
                Donor.name.ilike(f"%{search_term}%"),
                cast(Donor.id, String).ilike(f"%{search_term}%")  # Busca por ID convertido em texto
            ))

        return query.scalar()