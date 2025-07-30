# Makefile - Projeto BEES Breweries
# Uso:
#   make bronze                → executa a camada Bronze
#   make silver                → executa a camada Silver
#   make gold                  → executa a camada Gold
#   make verify                → executa todos os testes de verificação
#   make test                  → executa testes unitários com pytest
#   make duplicates            → verifica duplicatas na Silver
#   make eda-silver            → executa EDA na camada Silver
#   make eda-gold              → executa EDA na camada Gold
#   make verify-eda-silver     → executa EDA na Silver via Docker
#   make verify-eda-gold       → executa EDA na Gold via Docker
#   make verify-all            → executa todas as verificações via Docker
#   make all                   → executa bronze, silver, gold e verify

# Variáveis padrões
PROCESSING_DATE=$(shell date +%Y-%m-%d)
CARGA=delta
DELTA_DAYS=2
PYTHON=python3
PYTHONPATH=PYTHONPATH=./

# Caminhos dos scripts principais
BRONZE=./scripts/run_bronze.py
SILVER=./scripts/run_silver.py
GOLD=./scripts/run_gold.py
VERIFY=./scripts/verify_all.py

# Scripts de teste/validação
TEST_TRANSFORM=tests/test_transform.py
CHECK_DUPLICATES_SILVER=tests/check_duplicates_silver.py
CHECK_DUPLICATES_GOLD=tests/check_duplicates_gold.py
CHECK_EDA_SILVER=tests/check_eda_silver.py
CHECK_EDA_GOLD=tests/check_eda_gold.py

# Spark container (ajuste se necessário)
CONTAINER=spark-container

# Execução local via PYTHONPATH (recomendado fora do container)
bronze:
	$(PYTHONPATH) $(PYTHON) $(BRONZE)

silver:
	$(PYTHONPATH) $(PYTHON) $(SILVER)

gold:
	$(PYTHONPATH) $(PYTHON) $(GOLD)

verify:
	$(PYTHONPATH) $(PYTHON) $(VERIFY)

test:
	pytest $(TEST_TRANSFORM)

duplicates-silver:
	$(PYTHONPATH) $(PYTHON) $(CHECK_DUPLICATES_SILVER)

duplicates-gold:
	$(PYTHONPATH) $(PYTHON) $(CHECK_DUPLICATES_GOLD)

eda-silver:
	$(PYTHONPATH) $(PYTHON) $(CHECK_EDA_SILVER)

eda-gold:
	$(PYTHONPATH) $(PYTHON) $(CHECK_EDA_GOLD)

# Execução via Docker (usando PYTHONPATH=/home/project)
verify-eda-silver:
	docker exec -e PYTHONPATH=/home/project -it $(CONTAINER) \
	python3 /home/project/$(CHECK_EDA_SILVER)

verify-eda-gold:
	docker exec -e PYTHONPATH=/home/project -it $(CONTAINER) \
	python3 /home/project/$(CHECK_EDA_GOLD)

verify-all:
	docker exec -e PYTHONPATH=/home/project -it spark-container \
	python3 /home/project/tests/verify_all.py

# Executa tudo em sequência
all: bronze silver gold verify
