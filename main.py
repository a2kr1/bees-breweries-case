import os
import subprocess
from datetime import datetime, timedelta
from src.logger import setup_logger

logger = setup_logger()

# Define a data de processamento
delta_days = int(os.getenv("DELTA_DAYS", "0"))
processing_date = (datetime.now() + timedelta(days=delta_days)).strftime("%Y-%m-%d")
logger.info(f"📆 Data de processamento: {processing_date}")

# Exporta a variável de ambiente para os subprocessos
env = os.environ.copy()
env["PROCESSING_DATE"] = processing_date

def executar_etapa(script_name):
    path = f"/home/project/scripts/{script_name}"
    logger.info(f"🚀 Executando {script_name}...")
    result = subprocess.run(["python3", path], env=env, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"❌ Erro em {script_name}:\n{result.stderr}")
        raise RuntimeError(result.stderr)
    else:
        logger.info(f"✅ {script_name} executado com sucesso.\n{result.stdout}")

if __name__ == "__main__":
    try:
        executar_etapa("run_bronze.py")
        executar_etapa("run_silver.py")
        executar_etapa("run_gold.py")
        logger.info("🏁 Pipeline finalizado com sucesso.")
    except Exception as e:
        logger.error(f"❌ Falha na execução do pipeline: {e}")
