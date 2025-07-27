import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from src.api_client import fetch_breweries_from_api
from src.logger import logger  # 👈 Adicionar logger

if __name__ == "__main__":
    logger.info("🚀 Iniciando extração da camada Bronze...")

    per_page = 50
    max_pages = 200
    delay = 0.3

    fetch_breweries_from_api(per_page=per_page, max_pages=max_pages, delay=delay)

    logger.info("✅ Extração da camada Bronze finalizada.")
