# Makefile para orquestração local e containerizada do pipeline BEES

# Variáveis de ambiente padrão
PROCESSING_DATE ?= $(shell date +%F)
CARGA ?= append

# Caminhos
PYTHON ?= python
PROJECT_ROOT := $(PWD)

# Atalhos para execução local
run-bronze:
	$(PYTHON) scripts/run_bronze.py

run-silver:
	$(PYTHON) scripts/run_silver.py

run-gold:
	$(PYTHON) scripts/run_gold.py

run-all:
	$(PYTHON) scripts/main.py

test:
	pytest tests/

# Atalhos para execução com Docker
docker-bronze:
	docker exec -e CARGA=$(CARGA) -e PROCESSING_DATE=$(PROCESSING_DATE) -it spark-bees python3 /home/project/scripts/run_bronze.py

docker-silver:
	docker exec -e CARGA=$(CARGA) -e PROCESSING_DATE=$(PROCESSING_DATE) -it spark-bees python3 /home/project/scripts/run_silver.py

docker-gold:
	docker exec -e CARGA=$(CARGA) -e PROCESSING_DATE=$(PROCESSING_DATE) -it spark-bees python3 /home/project/scripts/run_gold.py

docker-all:
	docker exec -e CARGA=$(CARGA) -e PROCESSING_DATE=$(PROCESSING_DATE) -it spark-bees python3 /home/project/scripts/main.py

verify-bronze:
	docker exec -e PROCESSING_DATE=$(PROCESSING_DATE) -it spark-bees python3 /home/project/tests/verify_bronze.py

verify-silver:
	docker exec -e PROCESSING_DATE=$(PROCESSING_DATE) -it spark-bees python3 /home/project/tests/verify_silver.py

verify-gold:
	docker exec -e PROCESSING_DATE=$(PROCESSING_DATE) -it spark-bees python3 /home/project/tests/verify_gold.py
