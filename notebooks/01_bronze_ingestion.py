# Databricks notebook source
# MAGIC %md
# MAGIC ### 01 - Bronze Ingestion
# MAGIC
# MAGIC Ingestão de dados da API Open Brewery DB e salvamento dos arquivos no formato JSON particionados por data.

# COMMAND ----------
# Imports
import os
import requests
from datetime import datetime
from pathlib import Path
import logging

# COMMAND ----------
# Configurações e logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Diretórios
BASE_DIR = Path("/opt/landing")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Data atual para particionamento
processing_date = datetime.today().strftime("%Y-%m-%d")
output_path = BASE_DIR / processing_date
output_path.mkdir(exist_ok=True)

# API
API_URL = "https://api.openbrewerydb.org/breweries"

# COMMAND ----------
# Função para buscar todas as páginas
page = 1
records = 0

while True:
    logging.info(f"Buscando página {page} da API...")
    response = requests.get(API_URL, params={"page": page, "per_page": 50})

    if response.status_code != 200:
        logging.warning(f"Erro ao buscar dados da página {page}: {response.status_code}")
        break

    data = response.json()
    if not data:
        logging.info("Fim dos dados da API.")
        break

    file_path = output_path / f"breweries_page_{page}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)
        records += len(data)
        logging.info(f"Salvo: {file_path} ({len(data)} registros)")

    page += 1

logging.info(f"Ingestão finalizada. Total de registros: {records}")
