import subprocess
import os
from src.logger import setup_logger

logger = setup_logger()

tests = [
    "verify_bronze.py",
    "verify_silver.py",
    "verify_gold.py",
    "check_duplicates_silver.py",
    "check_duplicates_gold.py",
    "test_transform.py",
    "check_eda_silver.py",
    "check_eda_gold.py",
    "test_gold_qualify.py"    
]

logger.info("Iniciando verificações para ...")

for test in tests:
    logger.info(f"Executando verificação: {test}")

    test_path = f"/home/project/tests/{test}"
    if not os.path.exists(test_path):
        logger.warning(f"[SKIP] Arquivo não encontrado: {test_path}")
        continue

    result = subprocess.run(
        ["python3", test_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logger.error(f"Falha na verificação: {test}")
        logger.error(result.stderr)
    else:
        logger.info(f"✅ Verificação OK: {test}")
