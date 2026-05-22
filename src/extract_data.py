import json
import logging
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# endpoint do sistema gerenciador de series temporais do bcb
BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"

# nome da serie -> codigo sgs no banco central
SERIES = {
    "spread": 20783,
    "inadimplencia": 21082,
    "concessoes": 20631,
}


def extract_series(nome: str, codigo: int, output_dir: str) -> str:
    # puxa uma serie do bcb e salva como json local
    url = BCB_URL.format(codigo=codigo)
    logger.info(f"Extraindo {nome} (codigo {codigo})...")

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    path = Path(output_dir) / f"{nome}.json"
    path.write_text(json.dumps(data, ensure_ascii=False))

    logger.info(f"{nome}: {len(data)} registros salvos em {path}")
    return str(path)


def extract_all(output_dir: str = "data") -> dict[str, str]:
    # extrai as 3 series e retorna os caminhos dos arquivos gerados
    Path(output_dir).mkdir(exist_ok=True)
    paths = {}
    for nome, codigo in SERIES.items():
        paths[nome] = extract_series(nome, codigo, output_dir)
    return paths
