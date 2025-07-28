# 🍺 BEES Breweries Case

![CI](https://github.com/a2kr1/bees-breweries-case/actions/workflows/python-ci.yml/badge.svg)

Este projeto implementa uma solução completa para o case técnico da vaga de Engenheiro de Dados Sênior na BEES.  
A arquitetura adotada segue o padrão **Medallion** (Bronze, Silver, Gold), com **Airflow para orquestração**, **PySpark com Delta Lake para processamento** e **Docker para isolamento do ambiente**.

---

## 📄 Escopo oficial do case

Conforme instruções fornecidas:

1. **Consumir dados da API Open Brewery DB**  
2. **Aplicar arquitetura Medallion (Bronze, Silver, Gold)**  
3. **Persistência em Data Lake particionado por localização e data**  
4. **Orquestração com ferramenta como Airflow**  
5. **Testes automatizados**  
6. **Tratamento de erros e logging**  
7. **Containerização com Docker (bônus)**  
8. **Documentar design, trade-offs e instruções de execução**  
9. **Entregar em repositório público no GitHub com README completo**

---

## ✅ Entregas implementadas

| Requisito                           | Implementado | Local / Detalhes                                                   |
|------------------------------------|--------------|----------------------------------------------------------------------|
| Ingestão da API Open Brewery DB    | ✅           | `scripts/run_bronze.py`, `src/api_client.py`                        |
| Arquitetura Bronze → Silver → Gold| ✅           | Diretórios `data/bronze`, `data/silver`, `data/gold`                |
| Particionamento por data e estado  | ✅           | Via `["processing_date", "state"]`                                  |
| PySpark + Delta Lake               | ✅           | `src/transform.py`, `.write.format("delta")`, Delta Lake 2.4.0      |
| Orquestração com Airflow           | ✅           | `airflow/dags/brewery_dag.py`                                       |
| Logging estruturado com timezone   | ✅           | `src/logger.py` (America/Sao_Paulo)                                 |
| Tratamento robusto de erros        | ✅           | `try/except`, logs em todas as etapas                               |
| Testes automatizados               | ✅           | `tests/test_transform.py`, `tests/verify_*.py`, `verify_all.py`     |
| CI/CD com GitHub Actions           | ✅           | `.github/workflows/python-ci.yml`                                   |
| Containerização com Docker         | ✅           | `Dockerfile`, `docker-compose.yml`, execução via `spark-container`  |
| Documentação clara e completa      | ✅           | `README.md`, `SETUP.md`, `data_catalog.md`, Makefile                |

---

## 🗂️ Arquitetura Medallion

### 🟫 Bronze
- Leitura paginada da API Open Brewery DB
- Salvamento de arquivos JSON em: `/data/bronze/<processing_date>/`

### 🟪 Silver
- Leitura de múltiplos arquivos com tolerância a colunas ausentes
- Escrita em Delta Lake, com particionamento por `processing_date` e `state`
- Local: `/data/silver/processing_date=.../state=.../`

### 🟨 Gold
- Agregações por `state`, `brewery_type` e `processing_date`
- Escrita em Delta Lake com partições múltiplas
- Local: `/data/gold/processing_date=.../state=.../`

---

## 🧪 Testes e Qualidade

- Testes unitários em `tests/test_transform.py` com `pytest`
- Validação de camadas com `verify_bronze.py`, `verify_silver.py`, `verify_gold.py`
- Checagem de duplicatas em `tests/check_duplicates_silver.py`
- Verificação automatizada em `verify_all.py`

Executado via:

```bash
pytest tests/
# ou
python tests/verify_all.py
```

---

## ⚙️ Execução via Docker (recomendada)

```bash
docker compose build
docker compose up -d
```

Executar etapas manuais:

```bash
docker exec -e PROCESSING_DATE=2025-07-27 -it bees-breweries-case-spark-container-1 python3 /home/project/scripts/run_bronze.py
docker exec -e CARGA=append -e PROCESSING_DATE=2025-07-27 -it bees-breweries-case-spark-container-1 python3 /home/project/scripts/run_silver.py
docker exec -e CARGA=append -e PROCESSING_DATE=2025-07-27 -it bees-breweries-case-spark-container-1 python3 /home/project/scripts/run_gold.py
```

---

## 🧵 Execução local (alternativa)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/main.py
```

---

## 🎛️ Airflow

A DAG `brewery_dag.py` orquestra as 3 camadas em sequência.  
Local: `airflow/dags/brewery_dag.py`

---

## 📦 Estrutura de Projeto

- `scripts/` — Execução modular por camada (`run_*.py`, `main.py`)
- `src/` — Funções reutilizáveis e sessões Spark
- `tests/` — Testes unitários e validações
- `data/` — Camadas bronze/silver/gold organizadas por data e estado
- `.github/workflows/` — Pipeline CI/CD

---

## 🧠 Boas práticas adotadas

- Código modular e testável
- Logging padronizado com timezone
- Particionamento lógico e físico com múltiplas colunas
- Comentários automáticos nas colunas Delta (modo full)
- Pipeline validado com `Makefile` e `verify_all.py`

---

## 🧾 Catálogo de Dados

Disponível em [`data_catalog.md`](./data_catalog.md)

---

## 👨‍💻 Autor

**André Santos**  
Engenheiro de Dados | [GitHub](https://github.com/a2kr1)

---

## ✅ Repositório

https://github.com/a2kr1/bees-breweries-case
