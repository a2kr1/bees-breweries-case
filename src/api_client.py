import os
import json
import requests
from time import sleep
from dateutil import tz
from pytz import timezone
from datetime import datetime
from src.logger import setup_logger


logger = setup_logger()


def fetch_breweries_from_api(base_url: str, output_dir: str, max_pages: int = 200, per_page: int = 50, delay: float = 1.0):
    logger.info("🚀 Iniciando extração da camada Bronze...")
    logger.info(f"🕒 Data e Hora: {datetime.now(timezone('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')}")

    today = datetime.now(tz=tz.gettz("America/Sao_Paulo")).date().isoformat()
    output_dir = os.path.join(output_dir, today)
    os.makedirs(output_dir, exist_ok=True)

    consecutive_errors = 0

    for page in range(1, max_pages + 1):
        url = f"{base_url}?per_page={per_page}&page={page}"

        try:
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"⚠️ Falha ao buscar página {page}: {response.status_code}")
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    logger.error("❌ Três falhas consecutivas. Interrompendo extração.")
                    break
                continue

            data = response.json()
            if not data:
                logger.info(f"📭 Página {page} retornou vazia. Encerrando.")
                break

            file_path = os.path.join(output_dir, f"breweries_page_{page}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Página {page} salva com sucesso.")
            consecutive_errors = 0  # Reset após sucesso

            sleep(delay)

        except Exception as e:
            logger.error(f"❌ Erro ao buscar página {page}: {str(e)}")
            consecutive_errors += 1
            if consecutive_errors >= 3:
                logger.error("❌ Três falhas consecutivas. Interrompendo extração.")
                break
            continue

    logger.info("✅ Extração da camada Bronze finalizada.")
