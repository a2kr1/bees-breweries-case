# 🍺 BEES Breweries Case – Engenharia de Dados

Este projeto entrega uma solução completa de ingestão, transformação e análise de dados baseada na arquitetura Medallion (Bronze, Silver, Gold), utilizando PySpark, Delta Lake, Airflow e Docker.

---

## 🎯 Objetivo do Case

> “Consumir dados da API Open Brewery DB, transformá-los e persistir em um Data Lake estruturado em três camadas (raw, curated, analytics), com orquestração, containerização, testes e documentação.” – conforme especificado no PDF oficial `DE Case Atualizado.pdf`

---

## 🗂️ Arquitetura Medallion

### 🔹 Bronze Layer
- Ingestão de dados da API [Open Brewery DB](https://www.openbrewerydb.org/)
- Salvamento bruto em JSON por data (`data/bronze/YYYY-MM-DD/`)
- Paginado e robusto a falhas

### 🔸 Silver Layer
- Leitura dos arquivos JSON e unificação com tolerância a colunas ausentes
- Escrita em Delta Lake com particionamento por `processing_date`
- Criação da tabela `silver_breweries` com comentários de colunas

### 🟡 Gold Layer
- Agregação por `state`, `brewery_type`, `processing_date`
- Escrita em Delta Lake com tabela `gold_breweries`
- Comentários em colunas e particionamento físico

---

## ⚙️ Execução com Docker (recomendado)

```bash
# Subir os containers
docker compose build
docker compose up -d
```

### Executar as etapas manualmente (exemplo)

```bash
# Bronze
docker exec -e PROCESSING_DATE=2025-07-27 -it spark-bees python3 /home/project/scripts/run_bronze.py

# Silver
docker exec -e CARGA=append -e PROCESSING_DATE=2025-07-27 -it spark-bees python3 /home/project/scripts/run_silver.py

# Gold
docker exec -e CARGA=append -e PROCESSING_DATE=2025-07-27 -it spark-bees python3 /home/project/scripts/run_gold.py
```

---

## 📅 Parâmetros suportados

| Parâmetro         | Descrição                                                             |
|------------------|------------------------------------------------------------------------|
| `CARGA`           | Modo de carga: `full`, `append`, `delta`                              |
| `PROCESSING_DATE` | Data de referência no formato `YYYY-MM-DD`                            |
| `DELTA_DAYS`      | Quantos dias anteriores processar no modo `delta`                     |

---

## 🧪 Testes e Validações

### Testes unitários (PySpark)

```bash
pytest tests/
```

### Validações por camada

```bash
python tests/verify_bronze.py
python tests/verify_silver.py
python tests/verify_gold.py
python tests/check_duplicates_silver.py
```

### Validação completa

```bash
python tests/verify_all.py
```

---

## 🧵 Execução Local (modo `.venv`)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/main.py
```

---

## 📂 Organização dos Scripts

```bash
scripts/
├── run_bronze.py   # Extrai dados da API e salva JSON (camada Bronze)
├── run_silver.py   # Lê arquivos Bronze, transforma e escreve Delta (Silver)
├── run_gold.py     # Agrega e escreve tabela Gold particionada
├── main.py         # Orquestrador local: Bronze → Silver → Gold
```

Todos os scripts possuem função `main()` compatível com `import` e execução CLI.

---

## 🎛️ Airflow

DAG localizada em:

```bash
airflow/dags/brewery_dag.py
```

Configuração:
- Tarefa sequencial: Bronze → Silver → Gold
- BashOperator com execução em container Docker
- Suporte a `PROCESSING_DATE`, `CARGA`, `DELTA_DAYS`

---

## 🧠 Boas Práticas aplicadas

✅ Logging estruturado com timezone (America/Sao_Paulo)  
✅ Tratamento de erros com logs em todas as etapas  
✅ Scripts modulares com funções nomeadas  
✅ Estrutura de projeto clara e separação de camadas  
✅ Código testado e validado com `pytest` e `verify_all.py`  
✅ Compatível com Airflow, Docker, Makefile, e execução local  

---

## 🗃️ Catálogo de Dados

Ver detalhes em [`data_catalog.md`](./data_catalog.md)

---

## 👨‍💻 Autor

**André Santos** – Engenharia de Dados  
[LinkedIn](https://linkedin.com) • [GitHub](https://github.com)

---

## ✅ Status Final do Case

| Requisito do PDF | Implementado? | Observações |
|------------------|---------------|-------------|
| Ingestão API     | ✅            | Open Brewery DB via paginação |
| Bronze Layer     | ✅            | JSON bruto por data           |
| Silver Layer     | ✅            | Delta particionado + metadados |
| Gold Layer       | ✅            | Agregação por tipo e estado   |
| Orquestração     | ✅            | DAG no Airflow                |
| Docker           | ✅            | Com `compose` e container Spark |
| Logging/Erros    | ✅            | Logger estruturado em todas etapas |
| Testes           | ✅            | `pytest` + `verify_*` + `check_duplicates` |
| Documentação     | ✅            | README, SETUP.md, catálogo e Makefile |

---

## 📎 Recursos Extras

- `Makefile`: atalho para execução local e Docker
- `SETUP.md`: instruções detalhadas para setup e testes
- `.dockerignore`, `.gitignore` e `requirements.txt` configurados

---