# Rentflow: Glasgow Home Rental Pipeline/Dashboard

Rentflow is a project designed to compile and present all rental listings in Glasgow. The idea originated from my personal experience while searching for rental properties. This project showcases an end-to-end data pipeline, starting from data generation through web scraping, followed by data transformation, exporting data to a data warehouse, and ultimately building an interactive dashboard using Power BI.

![Pipeline Diagram drawio file](https://github.com/user-attachments/assets/19ff433c-1753-4c42-bd2d-de77879863be)


## Project Overview

1. **Data Collection**: Scrape rental listings from a website using Selenium.
2. **Data Enrichment**: Use the Google Maps API to find nearby train stations and calculate travel times by foot and train.
3. **Data Storage**: Store the transformed data in PostgreSQL and BigQuery.
4. **Data Visualization**: Create a visualization dashboard in Power BI to analyze the rental data.

## Tech Stack

- **Python**: Core programming language.
- **Selenium**: Web scraping tool to extract rental listings.
- **Google Maps API**: To find nearby train stations and calculate travel times.
- **Mage.ai**: Data orchestration tool.
- **PostgreSQL**: Relational database for storing transformed data.
- **BigQuery**: Data warehouse for large-scale data analysis.
- **Power BI**: Business analytics tool for data visualization.

## Project Structure

```plaintext
glasgow-rental-pipeline/
├── glasgow-home-rent/
    ├── data_exporters
        ├── rentflow_export_bigquery.py             # Data exporter for Google BigQuery
        ├── rentflow_export_postgres.py             # Data exporter for PostgreSQL
        ├── custom_data_exporter.py                 # Web scraper script for generating output.csv
    ├── data_loaders
        ├── ingest_data_from_csv.py                 # Loading data from the scraped csv
    ├── transformers
        ├── rentflow_gmap_integration.py            # Trasformer script for Google Maps data integration
        ├── rentflow_data_transformer.py            # Data cleaning and transformer script
├── dockerfile                                      # Scripts for docker build
├── docker-composy.yml/                             # Docker compose file for containerization
├── output.csv                                      # Web scraped data
├── requirements.txt                                # Python dependencies
└── README.md                                       # Project documentation
```

## Visualization (Power BI)
<img width="995" alt="image" src="https://github.com/ganeshs0504/glasgow-rental-pipeline/assets/145580150/81d579f5-4803-4eae-8444-23a7598813a5">

