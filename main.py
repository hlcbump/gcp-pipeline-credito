import os

from dotenv import load_dotenv

from src.extract_data import extract_all
from src.load_bigquery import load_gcs_to_bigquery
from src.load_gcs import upload_to_gcs

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID")
bucket = os.getenv("GCS_BUCKET")
dataset = os.getenv("BQ_DATASET")

# extract: api bcb -> json local
paths = extract_all()
print(f"\nArquivos gerados: {list(paths.values())}")

# load gcs: json local -> cloud storage
uploaded = upload_to_gcs(bucket, project_id)
print(f"\nUpload GCS concluido: {uploaded}")

# load bigquery: gcs -> tabelas raw
load_gcs_to_bigquery(project_id, dataset, uploaded)
print("\nLoad BigQuery concluido!")
