# 🍺 BEES Breweries Case

Este projeto implementa uma solução completa para o case técnico da vaga de Engenheiro de Dados Sênior na BEES.

A arquitetura segue o padrão **Medallion (Bronze, Silver, Gold)**, com orquestração em **Airflow**, processamento com **PySpark e Delta Lake**, testes automatizados, EDA e verificação de qualidade, tudo containerizado via **Docker**.

---

## 📄 Escopo oficial do case

1. Consumir dados da API Open Brewery DB
2. Aplicar arquitetura Medallion (Bronze, Silver, Gold)
3. Persistência em Data Lake particionado por data e localização
4. Orquestração com Airflow
5. Testes automatizados e EDA
6. Logging estruturado com tratamento de erros
7. Containerização com Docker
8. Verificação e validação de tabelas com `verify_all.py`
9. README completo com trade-offs e instruções

---

## ✅ Entregas implementadas

| Requisito                                   | Status ✅ | Local / Detalhes                                                   |
|--------------------------------------------|-----------|----------------------------------------------------------------------|
| Ingestão da API Open Brewery DB            | ✅         | `scripts/run_bronze.py`, `src/api_client.py`                        |
| Arquitetura Bronze → Silver → Gold         | ✅         | `data/{bronze,silver,gold}`                                         |
| Particionamento por `state` e `processing_date` | ✅         | Camadas Silver e Gold particionadas corretamente                     |
| PySpark + Delta Lake                       | ✅         | `src/transform.py`, `.write.format("delta")`                      |
| Orquestração com Airflow                   | ✅         | DAG em `airflow/dags/brewery_dag.py`                                |
| Logging estruturado com timezone           | ✅         | `src/logger.py` com fuso horário `America/Sao_Paulo`                |
| Tratamento robusto de erros                | ✅         | `try/except` em todos os scripts                                   |
| Testes automatizados e unitários           | ✅         | `tests/test_transform.py`, `tests/test_gold_quality.py`            |
| Verificação de duplicatas e metadados      | ✅         | `check_duplicates_silver.py`, `verify_gold.py`, `verify_all.py`    |
| EDA para Silver e Gold                     | ✅         | `check_eda_silver.py`, `check_eda_gold.py`                          |
| Containerização com Docker                 | ✅         | `Dockerfile`, `docker-compose.yml`                                  |
| Makefile de execução                       | ✅         | `Makefile` com targets `all`, `eda-silver`, `eda-gold`, etc         |

---

## 🗂️ Arquitetura Medallion

### 🟫 Bronze
- Ingestão paginada da API
- Salvamento em `/data/bronze/<processing_date>/breweries_page_<n>.json`

### 🟪 Silver
- Leitura resiliente de múltiplos arquivos JSON
- Escrita Delta particionada por `processing_date` e `state`
- Armazenamento: `/data/silver/processing_date=.../state=.../`

### 🟨 Gold
- Agregações por `state` e `brewery_type`, com `brewery_count`
- Escrita Delta com partição em `processing_date`
- Armazenamento: `/data/gold/processing_date=.../`

---

## 🧪 Testes, Verificações e Qualidade

- `pytest` com `test_transform.py`, `test_gold_quality.py`, `test_check_duplicates.py`
- `check_eda_silver.py` e `check_eda_gold.py` com detecção de outliers, nulos, cardinalidade e schema
- Validações por script: `verify_*.py`, `check_eda_*.py`, `check_duplicates_silver.py`
- Execução integrada no `verify_all.py` com logs limpos (sem emojis)

```bash
make verify
make test
make all
```

---

## ⚙️ Execução via Docker (recomendada)

```bash
docker compose build
docker compose up -d
```

### Manual via Docker:

```bash
docker exec -e PROCESSING_DATE=2025-07-29 -it spark-container python3 /home/project/scripts/run_bronze.py
docker exec -e CARGA=delta -e PROCESSING_DATE=2025-07-29 -it spark-container python3 /home/project/scripts/run_silver.py
docker exec -e CARGA=delta -e PROCESSING_DATE=2025-07-29 -it spark-container python3 /home/project/scripts/run_gold.py
docker exec -e PROCESSING_DATE=2025-07-29 -it spark-container python3 /home/project/tests/verify_all.py
```

---

## 🎛️ Airflow

DAG automatizada em `airflow/dags/brewery_dag.py`:

```text
run_bronze -> run_silver -> run_gold -> verify_tests
```

---

## 🧵 Execução local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
make all
```

---

## 📦 Estrutura de Projeto

- `scripts/`: scripts `run_bronze.py`, `run_silver.py`, `run_gold.py`, `main.py`
- `src/`: funções reutilizáveis (`logger`, `transform`, `api_client`)
- `tests/`: testes automatizados e de validação
- `data/`: estrutura Delta particionada por camada e data
- `airflow/`: configuração e DAG do Airflow
- `Makefile`: targets para facilitar execução local
- `.github/`: workflow CI/CD

---

## ✅ Repositório

https://github.com/a2kr1/bees-breweries-case

---

## 👨‍💻 Autor

**André Santos**  
Engenheiro de Dados | [GitHub](https://github.com/a2kr1)