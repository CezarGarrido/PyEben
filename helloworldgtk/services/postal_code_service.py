import requests
from typing import Optional

class Address:
    def __init__(self, street: Optional[str] = None, neighborhood: Optional[str] = None,
                 complement: Optional[str] = None, city: Optional[str] = None,
                 state: Optional[str] = None, postal_code: Optional[str] = None,
                 number: Optional[str] = None, country: str = "Brazil"):
        self.street = street
        self.neighborhood = neighborhood
        self.complement = complement
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.number = number
        self.country = country

    @classmethod
    def fetch(cls, postal_code: str) -> "Address":
        url = f"https://viacep.com.br/ws/{postal_code}/json/"
        response = requests.get(url, headers={"Content-Type": "application/json"}, verify=False)  # Desativa verificação SSL
        
        if response.status_code == 200:
            data = response.json()
            return cls(
                street=data.get("logradouro"),
                neighborhood=data.get("bairro"),
                complement=data.get("complemento"),
                city=data.get("localidade"),
                state=data.get("uf"),
                postal_code=data.get("cep")
            )
        else:
            raise Exception(f"Erro ao consultar o ViaCEP: {response.status_code}")

# Exemplo de uso:
if __name__ == "__main__":
    try:
        address = Address.fetch("79823010")
        print(vars(address))
    except Exception as e:
        print(e)
