
# ⚙️ SETUP.md - Inicialização e Testes do Projeto

Este arquivo contém os comandos e instruções para configurar, rodar e testar o pipeline de dados da BEES (Open Brewery Case).

---

## 🛠️ Instalação Local (modo .venv)

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 🧪 Rodar pipeline completo

```bash
python scripts/main.py
```

---

## 📆 Rodar com DELTA_DAYS ou PROCESSING_DATE

```bash
# Usar DELTA_DAYS para reprocessar N dias atrás
SET DELTA_DAYS=1
python scripts/main.py

# Usar data fixa
SET PROCESSING_DATE=2025-07-27
python scripts/main.py
```

---

## 🧪 Testes com Pytest

```bash
pytest tests/
```

---

## 🐳 Docker

```bash
docker compose build
docker compose up -d
docker exec -it spark-bees bash
```

Executar pipeline no container:

```bash
docker exec -it spark-bees python3 /home/project/scripts/main.py
```

---

## 📂 Limpeza (local)

```bash
rm -rf data/bronze/* data/silver/* data/gold/*
```

---

## 🔄 Verificação das camadas

```bash
docker exec -e PROCESSING_DATE=2025-07-27 -it spark-bees python3 /home/project/tests/verify_bronze.py
docker exec -e PROCESSING_DATE=2025-07-27 -it spark-bees python3 /home/project/tests/verify_silver.py
docker exec -e PROCESSING_DATE=2025-07-27 -it spark-bees python3 /home/project/tests/verify_gold.py
```

---

## 📌 Observações

- Fuso horário: America/Sao_Paulo
- Formato de data: YYYY-MM-DD
- Suporte total a Airflow + Git + Docker + VS Code
