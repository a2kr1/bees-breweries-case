import os
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from src.api_client import fetch_breweries_from_api
from src.logger import logger
from src.transform import create_spark_session
import json
from pathlib import Path

def main():
    spark = create_spark_session("BronzeExtraction")

    carga = os.getenv("CARGA", "append").lower()
    delta_days = int(os.getenv("DELTA_DAYS", 0))
    processing_date = (datetime.now() - timedelta(days=delta_days)).strftime("%Y-%m-%d")

    logger.info(f"⚙️ Modo de carga: {carga}")
    logger.info(f"📅 Data de processamento Bronze: {processing_date}")

    output_dir = Path(f"/home/project/data/bronze/{processing_date}")
    output_dir.mkdir(parents=True, exist_ok=True)

    pagina_inicial = 1
    pagina_final = 1000
    arquivos_salvos = 0

    for pagina in range(pagina_inicial, pagina_final + 1):
        try:
            breweries = fetch_breweries_from_api(pagina)
            if not breweries:
                logger.info(f"📭 Página {pagina} retornou vazia. Encerrando extração.")
                break

            output_file = output_dir / f"breweries_page_{pagina}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(breweries, f, ensure_ascii=False, indent=2)

            arquivos_salvos += 1
            logger.info(f"💾 Página {pagina} salva em {output_file}")

        except Exception as e:
            logger.error(f"❌ Erro ao processar página {pagina}: {e}")
            break

    if arquivos_salvos == 0:
        logger.warning("⚠️ Nenhum dado foi salvo na camada Bronze.")
    else:
        logger.info(f"✅ Extração finalizada. {arquivos_salvos} páginas salvas em {output_dir}")

if __name__ == "__main__":
    main()
