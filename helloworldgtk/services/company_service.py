from models.company import Company
from database import Session

class CompanyService:
    def listar_todas(self):
        session = Session()
        empresas = session.query(Company).all()
        session.close()
        return empresas