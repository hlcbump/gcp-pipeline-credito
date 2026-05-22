import json
import logging
import os
import tempfile
from pathlib import Path

import functions_framework
import requests
from google.cloud import bigquery, storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "credito-pipeline-br")
BUCKET_NAME = os.environ.get("GCS_BUCKET", "credito-pipeline-raw-br")
BQ_DATASET = os.environ.get("BQ_DATASET", "credito")

BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"

SERIES = {
    "spread": 20783,
    "inadimplencia": 21082,
    "concessoes": 20631,
}

RAW_TABLES = {
    "spread": "raw_spread",
    "inadimplencia": "raw_inadimplencia",
    "concessoes": "raw_concessoes",
}


def extract_series(nome, codigo, output_dir):
    url = BCB_URL.format(codigo=codigo)
    logger.info(f"extraindo {nome} (codigo {codigo})...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    path = Path(output_dir) / f"{nome}.json"
    path.write_text(json.dumps(data, ensure_ascii=False))
    logger.info(f"{nome}: {len(data)} registros")
    return str(path)


def upload_to_gcs(json_path, bucket_name):
    data = json.loads(Path(json_path).read_text())
    ndjson_path = json_path.replace(".json", ".ndjson")
    with open(ndjson_path, "w") as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob_name = f"raw/{Path(ndjson_path).name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(ndjson_path)
    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    logger.info(f"upload: {ndjson_path} -> {gcs_uri}")
    return gcs_uri


def load_to_bigquery(serie, gcs_uri):
    client = bigquery.Client(project=PROJECT_ID)
    table_name = RAW_TABLES[serie]
    table_id = f"{PROJECT_ID}.{BQ_DATASET}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=[
            bigquery.SchemaField("data", "STRING"),
            bigquery.SchemaField("valor", "STRING"),
        ],
    )

    load_job = client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
    load_job.result()
    table = client.get_table(table_id)
    logger.info(f"{table_name}: {table.num_rows} linhas carregadas")


@functions_framework.http
def ingest_credito(request):
    with tempfile.TemporaryDirectory() as tmp_dir:
        for nome, codigo in SERIES.items():
            json_path = extract_series(nome, codigo, tmp_dir)
            gcs_uri = upload_to_gcs(json_path, BUCKET_NAME)
            load_to_bigquery(nome, gcs_uri)

    return {"status": "ok", "series": list(SERIES.keys())}, 200
