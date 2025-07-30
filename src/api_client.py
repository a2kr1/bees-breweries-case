import os
import json
import time
import requests
from datetime import datetime
from src.logger import logger

def fetch_breweries_from_api(
    base_url: str = "https://api.openbrewerydb.org/v1/breweries",
    output_dir: str = "data/bronze",
    per_page: int = 50,
    delay: float = 1.0,
    processing_date: str = None
) -> None:
    """
    Extrai dados da API Open Brewery DB página a página até não haver mais dados.
    Cada página é salva como um arquivo JSON separado na pasta de saída.
    """
    pagina = 1
    falhas_consecutivas = 0
    max_falhas = 3
    registros_total = 0
    paginas_total = 0

    os.makedirs(output_dir, exist_ok=True)
    data_extracao = processing_date or datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Extraindo dados da API: {base_url}")

    while True:
        url = f"{base_url}?per_page={per_page}&page={pagina}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            registros_total += len(data)
            paginas_total += 1

            nome_arquivo = os.path.join(
                output_dir,
                f"{data_extracao}/breweries_page_{pagina}.json"
            )
            os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            pagina += 1
            falhas_consecutivas = 0
            time.sleep(delay)

        except Exception as e:
            falhas_consecutivas += 1
            logger.error(f"Erro ao buscar página {pagina}: {e}")
            if falhas_consecutivas >= max_falhas:
                logger.error("Três falhas consecutivas. Interrompendo extração.")
                break
            else:
                time.sleep(delay * 2)

    logger.info(f"Extração da camada Bronze finalizada: {paginas_total} páginas, {registros_total} registros salvos.")
