import logging
from logging import StreamHandler, Formatter
from datetime import datetime
from pytz import timezone

def setup_logger():
    logger = logging.getLogger("custom_logger")
    logger.setLevel(logging.INFO)

    # Evita múltiplos handlers se o logger já tiver sido configurado
    if not logger.handlers:
        handler = StreamHandler()
        formatter = Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# ⬇️ Exportando diretamente para facilitar o import
logger = setup_logger()

# ⬇️ Alterando o timezone para América/São_Paulo
class TzFormatter(Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone("America/Sao_Paulo"))
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

logger.handlers[0].setFormatter(
    TzFormatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
)
