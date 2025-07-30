
# 📘 Documentação Técnica – Projeto BEES Breweries Case

Este documento apresenta as principais decisões técnicas, arquitetura e estratégias utilizadas no desenvolvimento do case técnico de Engenharia de Dados para a BEES.

---

## 🔧 Escolhas Técnicas

### 1. PySpark + Delta Lake como Plataforma Principal
- Utilização do PySpark como motor de processamento distribuído.
- Armazenamento com Delta Lake em disco local, permitindo versionamento, transações ACID e escrita particionada.
- Ideal para simular um ambiente de produção mesmo sem Databricks.

### 2. Armazenamento Local com Delta Lake
- Os dados foram salvos em disco no formato Delta, organizados por camadas e particionados por `processing_date` e `state`.
- Benefícios:
  - Desempenho otimizado para leitura e escrita.
  - Facilidade para simular ambiente Data Lake em arquitetura Medallion.
  - Permite auditoria e rollback com controle de versão de dados.

### 3. Orquestração com Apache Airflow
- Utilização do Airflow com DAG única (`brewery_dag.py`) para orquestrar todo o pipeline.
- Execução sequencial: Bronze → Silver → Gold → Verificações
- Flexibilidade para execução agendada ou manual.

### 4. Containerização com Docker
- Todo o projeto pode ser executado via `docker-compose`.
- Criação de ambiente isolado, com dependências resolvidas.
- Inclui serviços de Spark, Airflow, e dashboard EDA.

---

## 🏗️ Arquitetura em Camadas (Medallion)

### 🟫 Bronze
- Ingestão direta da API Open Brewery DB (paginada).
- Armazenamento de arquivos JSON brutos com controle por data.

### 🟪 Silver
- Leitura resiliente dos arquivos da Bronze.
- Normalização dos dados e escrita em formato Delta particionado por `processing_date` e `state`.
- Aplicação de regras de schema e eliminação de duplicatas.

### 🟨 Gold
- Agregações analíticas por `state` e `brewery_type`.
- Escrita em Delta particionado por `processing_date`.

---

## 📑 Metadados e Versionamento

### Armazenamento Delta
- Cada tabela Delta permite versionamento e histórico de alterações (Time Travel).
- Acesso a snapshots com controle de schema evolution.

### Metadados
- Estrutura padrão adotada para as colunas (ex: nomes consistentes entre camadas).
- Utilização de comentários nas colunas no modo `full` para documentação via `ALTER COLUMN`.

---

## 🧪 Verificações de Qualidade

- Scripts automatizados de validação com `pytest` e `verify_all.py`.
- Verificações implementadas:
  - Existência de dados
  - Presença de valores nulos
  - Checagem de duplicatas
  - Validação de schema

---

## 📊 Dashboard EDA

- Visualização simples via HTML, acessível em: `http://localhost:8080/eda`
- Página estática configurada via `webserver_config.py` no Airflow.
- Possível integração com dados da Silver em tempo real.

---

## ⚙️ Execução

### Via Docker
```bash
docker compose build
docker compose up -d
```

### Execução manual por container
```bash
docker exec -e PROCESSING_DATE=2025-07-30 -it spark-container python3 /home/project/scripts/run_bronze.py
docker exec -e PROCESSING_DATE=2025-07-30 -e CARGA=delta -it spark-container python3 /home/project/scripts/run_silver.py
docker exec -e PROCESSING_DATE=2025-07-30 -e CARGA=delta -it spark-container python3 /home/project/scripts/run_gold.py
docker exec -e PROCESSING_DATE=2025-07-30 -it spark-container python3 /home/project/tests/verify_all.py
```

---

## 📁 Estrutura dos Diretórios

```
bees-breweries-case/
├── airflow/
│   ├── dags/
│   ├── static/
│   └── config/webserver_config.py
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── scripts/
├── src/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

---

## 👨‍💻 Autor

**André Santos**  
Engenheiro de Dados | [github.com/a2kr1](https://github.com/a2kr1)
