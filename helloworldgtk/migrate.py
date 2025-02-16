from alembic import command
from alembic.config import Config
import sys
import os

def run_migrations():
    alembic_ini_path = get_resource_path("alembic.ini")
    migrations_path = get_resource_path("alembic")

    config = Config(alembic_ini_path)
    config.set_main_option("script_location", migrations_path)
    
    command.upgrade(config, "head")  # Aplica todas as migrações

def get_resource_path(relative_path):
    """Retorna o caminho do recurso, lidando com execução via PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Quando rodando como executável, os arquivos são extraídos em _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)
