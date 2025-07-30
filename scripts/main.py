import os
from src.logger import setup_logger
from scripts import run_bronze, run_silver, run_gold

logger = setup_logger("main")

if __name__ == "__main__":
    try:
        logger.info("Iniciando pipeline completo (Bronze → Silver → Gold)")
        run_bronze.main()
        run_silver.main()
        run_gold.main()
        logger.info("Pipeline executado com sucesso.")
    except Exception as e:
        logger.error(f"Erro durante a execução do pipeline completo: {e}")
        raise
