from sqlalchemy.orm import Session
from ..models.employee import Employee, EmployeeContact
from ..database import Session
from ..models.user import User

class EmployeeService:
    def __init__(self):
        self.db = Session()

    def create_employee(self, user: User, new_employee: Employee):
        """
        Cria um novo usuário na mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param new_user: Objeto User contendo os dados do novo usuário.
        :return: ID do novo usuário criado.
        """
        new_employee.company_id = user.company_id  # Garante que o novo usuário pertença à mesma empresa
        new_employee.user_creator_id = user.id  # Registra o criador do usuário

        self.db.add(new_employee)
        self.db.commit()
        self.db.refresh(new_employee)
        return new_employee.id
    
    def list(self, user: User):
        """
        Lista todos os usuários da mesma empresa do usuário fornecido.
        :param user: Usuário autenticado que está fazendo a requisição.
        :return: Lista de instâncias de User da mesma empresa.
        """
        return self.db.query(Employee).filter(Employee.company_id == user.company_id).all()

    def get_by_id(self, user: User, user_id: int):
        """
        Obtém um usuário pelo ID, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param user_id: ID do usuário a ser buscado.
        :return: Instância de User se encontrado e pertencente à mesma empresa, None caso contrário.
        """
        return self.db.query(Employee).filter(Employee.id == user_id, Employee.company_id == user.company_id).first()

    def update(self, user: User, updated_employee: Employee):
        existing = self.get_by_id(user, updated_employee.id)
        if existing:
            self.db.query(EmployeeContact).filter_by(employee_id=updated_employee.id).delete()
            self.db.merge(updated_employee)
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
