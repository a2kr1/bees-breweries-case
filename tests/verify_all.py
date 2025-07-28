import os
import sys
import subprocess
from datetime import datetime
from src.logger import logger


def get_processing_date():
    return os.getenv("PROCESSING_DATE", datetime.today().strftime("%Y-%m-%d"))


def run_verification(script_name: str):
    try:
        logger.info(f"🔍 Executando verificação: {script_name}")
        exit_code = os.system(f"python3 tests/{script_name}")
        if exit_code != 0:
            logger.error(f"❌ Falha na verificação: {script_name}")
            return False
        logger.info(f"✅ Verificação OK: {script_name}")
        return True
    except Exception as e:
        logger.error(f"⚠️ Erro ao rodar {script_name}: {e}")
        return False


def run_pytest():
    try:
        logger.info("🧪 Executando testes unitários (pytest/test_transform.py)...")
        result = subprocess.run(["pytest", "tests/test_transform.py"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ Testes unitários falharam.")
            print(result.stdout)
            print(result.stderr)
            return False
        logger.info("✅ Testes unitários passaram com sucesso.")
        return True
    except Exception as e:
        logger.error(f"⚠️ Erro ao executar pytest: {e}")
        return False


def run_check_duplicates():
    try:
        logger.info("🔁 Verificando duplicatas na Silver...")
        exit_code = os.system("python3 tests/check_duplicates_silver.py")
        if exit_code != 0:
            logger.warning("⚠️ Verificação de duplicatas retornou erro.")
            return False
        logger.info("✅ Verificação de duplicatas finalizada com sucesso.")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao verificar duplicatas: {e}")
        return False


if __name__ == "__main__":
    processing_date = get_processing_date()
    os.environ["PROCESSING_DATE"] = processing_date
    logger.info(f"📅 Iniciando verificações para {processing_date}...")

    steps = [
        "verify_bronze.py",
        "verify_silver.py",
        "verify_gold.py"
    ]

    all_passed = True

    for script in steps:
        if not run_verification(script):
            all_passed = False

    if not run_check_duplicates():
        all_passed = False

    if not run_pytest():
        all_passed = False

    if all_passed:
        logger.info("✅ Todas as verificações e testes passaram com sucesso.")
        sys.exit(0)
    else:
        logger.error("❌ Uma ou mais etapas falharam.")
        sys.exit(1)
