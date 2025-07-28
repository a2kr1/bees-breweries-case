
# 📚 Catálogo de Dados - BEES Brewery Case

Este documento descreve o schema e as colunas presentes nas camadas Silver e Gold do projeto de engenharia de dados baseado na API Open Brewery DB.

---

## 🟦 Silver Layer (`data/silver/`)

| Coluna            | Tipo       | Descrição                                                |
|-------------------|------------|----------------------------------------------------------|
| id                | string     | Identificador único da cervejaria (UUID)                 |
| name              | string     | Nome da cervejaria                                       |
| brewery_type      | string     | Tipo da cervejaria (ex: micro, brewpub)                  |
| address_1         | string     | Endereço principal                                       |
| address_2         | string     | Endereço adicional (linha 2)                             |
| address_3         | string     | Endereço adicional (linha 3)                             |
| city              | string     | Cidade da cervejaria                                     |
| state_province    | string     | Estado ou província                                      |
| postal_code       | string     | Código postal                                            |
| country           | string     | País                                                     |
| longitude         | double     | Longitude geográfica                                     |
| latitude          | double     | Latitude geográfica                                      |
| phone             | string     | Telefone da cervejaria                                   |
| website_url       | string     | URL oficial da cervejaria                                |
| state             | string     | Estado (às vezes duplicado com state_province)           |
| street            | string     | Endereço completo em formato livre                       |
| ingestion_date    | timestamp  | Timestamp da ingestão do JSON original                   |
| silver_load_date  | timestamp  | Timestamp de carregamento na camada Silver               |
| processing_date   | string     | Data da partição de processamento (`YYYY-MM-DD`)         |

---

## 🟨 Gold Layer (`data/gold/`)

| Coluna            | Tipo       | Descrição                                                |
|-------------------|------------|----------------------------------------------------------|
| state             | string     | Estado                                                   |
| brewery_type      | string     | Tipo de cervejaria                                       |
| brewery_count     | bigint     | Contagem de cervejarias por tipo e estado                |
| gold_load_date    | timestamp  | Timestamp de carregamento da camada Gold                |

---

⏱️ Última atualização: automática via script - projeto BEES ETL
