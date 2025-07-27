## 🐳 Executando com Docker

```bash
# Build
docker compose build

# Subir o container
docker compose up -d

# Entrar no container
docker exec -it spark-bees bash
```

---

## 🛠️ Execução Manual do Pipeline

### Bronze

Executa a ingestão da API Open Brewery DB para a camada Bronze:

```bash
python3 scripts/run_bronze.py
```

### Silver

Transforma os dados da camada Bronze para a camada Silver, tratando duplicidades, particionando por localização e armazenando no formato Delta Lake:

```bash
# Processamento com data de hoje (default)
docker exec -it spark-bees python3 /home/project/scripts/run_silver.py

# Processamento com DELTA_DAYS (ex: -1 para ontem)
docker exec -e DELTA_DAYS=-1 -it spark-bees python3 /home/project/scripts/run_silver.py

# Reprocessamento com data fixa (ex: 2025-07-26)
docker exec -e PROCESSING_DATE=2025-07-26 -it spark-bees python3 /home/project/scripts/run_silver.py
```

### Gold

Cria uma visão analítica agregada da Silver:

```bash
# Agregação por tipo e estado (data de hoje)
docker exec -it spark-bees python3 /home/project/scripts/run_gold.py

# Agregação por data fixa
docker exec -e PROCESSING_DATE=2025-07-26 -it spark-bees python3 /home/project/scripts/run_gold.py
```

---

## ✅ Validação Manual Pós-Pipeline

Utilize os scripts da pasta `/tests/` para validar os dados processados:

### Silver

```bash
docker exec -e PROCESSING_DATE=2025-07-26 -it spark-bees python3 /home/project/tests/verify_silver.py
```

### Gold

```bash
docker exec -e PROCESSING_DATE=2025-07-26 -it spark-bees python3 /home/project/tests/verify_gold.py
```

(🔜 Em breve: `verify_bronze.py`)

Cada script valida:

* Existência do diretório Delta
* Leitura correta do formato Delta
* Contagem de registros
* (Silver) Ausência de duplicidades com base na chave primária `id`

---

## 🔑 Chave Primária e Deduplicação

A chave primária utilizada para validação de integridade e deduplicação na camada Silver é:

```text
id  # UUID único da cervejaria (conforme documentação da Open Brewery DB)
```

---

## 🧱 Arquitetura Medallion

Este projeto segue o padrão Medallion (Bronze, Silver, Gold):

* **Bronze:** Dados crus da API.
* **Silver:** Dados estruturados e particionados por localização, com deduplicação e validação.
* **Gold:** Visão analítica agregada com quantidade de cervejarias por tipo (`brewery_type`) e estado (`state`).

---

## 📋 Checklist de Validação Pós-Pipeline

1. ✅ A execução foi finalizada sem erros no log?
2. ✅ O diretório da Silver foi criado para a data correta?
3. ✅ Existe `_delta_log` no diretório da Silver (formato Delta válido)?
4. ✅ Há registros gravados (`count() > 0`)?
5. ✅ Não há duplicidades na chave primária `id`?
6. ✅ Gold foi atualizada corretamente com agregações por `brewery_type` e `state`?

---

## 🔍 Referência da API

* [Open Brewery DB](https://www.openbrewerydb.org/documentation/01-listbreweries)

---

## ✍️ Observações

* Use `DELTA_DAYS` para agendamento dinâmico (hoje, ontem, etc.)
* Use `PROCESSING_DATE` para reprocessamentos específicos
* Preferencialmente use apenas um dos dois para evitar conflitos
