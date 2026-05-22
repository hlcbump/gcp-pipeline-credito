import json
import logging
from pathlib import Path

from google.cloud import storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


def convert_to_ndjson(json_path: str) -> str:
    # bigquery espera ndjson (1 objeto por linha), nao array json
    data = json.loads(Path(json_path).read_text())
    ndjson_path = json_path.replace(".json", ".ndjson")
    with open(ndjson_path, "w") as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    logger.info(f"convertido {json_path} -> {ndjson_path} ({len(data)} linhas)")
    return ndjson_path


def upload_to_gcs(bucket_name: str, project_id: str = None, source_dir: str = "data") -> dict[str, str]:
    # sobe os ndjsons pro bucket no cloud storage
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    uploaded = {}

    for json_path in sorted(Path(source_dir).glob("*.json")):
        ndjson_path = convert_to_ndjson(str(json_path))
        blob_name = f"raw/{Path(ndjson_path).name}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(ndjson_path)
        gcs_uri = f"gs://{bucket_name}/{blob_name}"
        uploaded[json_path.stem] = gcs_uri
        logger.info(f"upload: {ndjson_path} -> {gcs_uri}")

    return uploaded
