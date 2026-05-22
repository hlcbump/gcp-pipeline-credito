import logging
from datetime import datetime, timezone

from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# tabelas raw que vou criar no bigquery, uma por serie
TABLES = {
    "spread": "raw_spread",
    "inadimplencia": "raw_inadimplencia",
    "concessoes": "raw_concessoes",
}


def load_gcs_to_bigquery(
    project_id: str, dataset: str, gcs_uris: dict[str, str]
) -> None:
    # carrega os ndjsons do gcs como tabelas no bigquery
    client = bigquery.Client(project=project_id)

    for serie, gcs_uri in gcs_uris.items():
        table_name = TABLES[serie]
        table_id = f"{project_id}.{dataset}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=[
                bigquery.SchemaField("data", "STRING"),
                bigquery.SchemaField("valor", "STRING"),
            ],
        )

        logger.info(f"carregando {gcs_uri} -> {table_id}...")
        load_job = client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
        load_job.result()

        table = client.get_table(table_id)
        logger.info(f"{table_name}: {table.num_rows} linhas carregadas")
