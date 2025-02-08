from sqlalchemy.orm import Session
from ..models.user import User
from ..database import Session

class UserService:
    def __init__(self):
        self.db = Session()

    def login(self, username, password):
        """
        Realiza o login do usuário e retorna um objeto User caso bem-sucedido.
        :param username: Nome de usuário.
        :param password: Senha fornecida.
        :return: Instância de User se o login for bem-sucedido, ou None se falhar.
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if user and User.check_password(password, user.password):
            return user  # O objeto User já inclui a Role automaticamente
        
        raise ValueError("Usuário ou senha inválidos")

    def list_users(self, user: User):
        """
        Lista todos os usuários da mesma empresa do usuário fornecido.
        :param user: Usuário autenticado que está fazendo a requisição.
        :return: Lista de instâncias de User da mesma empresa.
        """
        return self.db.query(User).filter(User.company_id == user.company_id).all()

    def get_user_by_id(self, user: User, user_id: int):
        """
        Obtém um usuário pelo ID, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param user_id: ID do usuário a ser buscado.
        :return: Instância de User se encontrado e pertencente à mesma empresa, None caso contrário.
        """
        return self.db.query(User).filter(User.id == user_id, User.company_id == user.company_id).first()

    def create_user(self, user: User, new_user: User):
        """
        Cria um novo usuário na mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param new_user: Objeto User contendo os dados do novo usuário.
        :return: ID do novo usuário criado.
        """
        new_user.company_id = user.company_id  # Garante que o novo usuário pertença à mesma empresa
        new_user.user_creator_id = user.id  # Registra o criador do usuário

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user.id

    def update_user(self, user: User, updated_user: User):
        """
        Atualiza os dados de um usuário no banco de dados, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param updated_user: Objeto User contendo os dados atualizados.
        :return: Booleano indicando se a atualização foi bem-sucedida.
        """
        existing_user = self.get_user_by_id(user, updated_user.id)
        if existing_user:
            self.db.merge(updated_user)
            self.db.commit()
            return True
        return False

    def deactivate_user(self, user: User, user_id: int):
        """
        Desativa um usuário pelo ID, alterando seu status, desde que pertença à mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param user_id: ID do usuário a ser desativado.
        :return: Booleano indicando se a operação foi bem-sucedida.
        """
        user_to_deactivate = self.get_user_by_id(user, user_id)
        if user_to_deactivate:
            user_to_deactivate.active = False
            self.db.commit()
            return True
        return False
