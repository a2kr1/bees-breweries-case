from datetime import datetime
import os
from src.api_client import fetch_breweries_from_api
from src.logger import logger
from src.utils import get_timezone_aware_date

if __name__ == "__main__":
    try:
        logger.info("Iniciando extração da camada Bronze...")

        # Define a data de processamento com base no fuso horário UTC-3 (America/Sao_Paulo)
        processing_date = os.environ.get("PROCESSING_DATE")
        if not processing_date:
            processing_date = get_timezone_aware_date("America/Sao_Paulo")

        input_path = os.path.join("data", "bronze")

        logger.info(f"Data de processamento Bronze: {processing_date}")

        fetch_breweries_from_api(
            output_dir=input_path,
            processing_date=processing_date
        )

    except Exception as e:
        logger.exception(f"Erro durante a execução da Bronze: {e}")
