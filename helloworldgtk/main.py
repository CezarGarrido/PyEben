import os
from .application import Application
from .models.base import Base
import logging
import structlog
import json
from logging.handlers import TimedRotatingFileHandler

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Garante que a pasta existe

# Configuração do handler para rotação diária
log_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_dir, "log"),  # Caminho do log
    when="m",    # Rotação diária
    interval=1,         # A cada 1 dia
    backupCount=7,      # Mantém os últimos 7 dias de logs
    encoding="utf-8",
    utc=True
)

# Configurar o formatador JSON para o handler
class StructlogJSONFormatter(logging.Formatter):
    def format(self, record):
        """ Formata o log como JSON usando structlog. """
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_entry, ensure_ascii=False)

# Adicionando formatador JSON ao handler
log_handler.setFormatter(StructlogJSONFormatter())

# Configuração do logging básico
logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler]
)

# Configuração do structlog para JSON
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),  # Timestamp ISO 8601
        structlog.processors.JSONRenderer(),           # Garante saída 100% JSON
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

def main(argv):
    app = Application()
    app.run(argv)