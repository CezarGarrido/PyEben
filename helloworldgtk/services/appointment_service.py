from sqlalchemy import extract
from sqlalchemy.orm import Session
from ..models.appointment import Appointment
from ..database import Session
from ..models.user import User

class AppointmentService:
    def __init__(self):
        self.db = Session()

    def list(self, user: User):
        """
        Lista todos os usuários da mesma empresa do usuário fornecido.
        :param user: Usuário autenticado que está fazendo a requisição.
        :return: Lista de instâncias de User da mesma empresa.
        """
        return self.db.query(Appointment).filter(Appointment.company_id == user.company_id).all()
    
    def create(self, user: User, new_appoitment: Appointment):
        """
        Cria um novo usuário na mesma empresa do usuário autenticado.
        :param user: Usuário autenticado que está fazendo a requisição.
        :param new_user: Objeto User contendo os dados do novo usuário.
        :return: ID do novo usuário criado.
        """
        new_appoitment.company_id = user.company_id  # Garante que o novo usuário pertença à mesma empresa
        new_appoitment.user_creator_id = user.id  # Registra o criador do usuário

        self.db.add(new_appoitment)
        self.db.commit()
        self.db.refresh(new_appoitment)
        return new_appoitment.id
    
    def get_appointments_by_date(self, user: User, date):
        """Retorna os compromissos de uma empresa para uma determinada data."""
        return self.db.query(Appointment).filter(
            Appointment.company_id == user.company_id,
            extract('year', Appointment.date) == date.year,
            extract('month', Appointment.date) == date.month,
            extract('day', Appointment.date) == date.day
        ).all()

    def delete_appointment(self, user: User, appointment_id):
        print("de")
