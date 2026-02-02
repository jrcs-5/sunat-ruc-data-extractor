import pandas as pd
import logging
import json
import os
import hashlib

logger = logging.getLogger(__name__)


INPUT_DIR = "data\input"
OUTPUT_DIR = "data\output"
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.json")



def get_rucs(filename: str, column_name: str):
    ruta = os.path.join(INPUT_DIR, filename)
    logger.info(f"Leyendo archivo: {ruta}")
    df = pd.read_excel(ruta, dtype=str)
    if df.empty:
        raise ValueError("El archivo está vacío")
    if column_name not in df.columns:
        raise ValueError(f"La columna '{column_name}' no existe")
    rucs = (df[column_name].dropna().astype(str).str.strip().drop_duplicates().tolist())
    logger.info(f"Total de RUCs únicos: {len(rucs)}")
    return rucs


def calcular_hash_archivo(filename: str) -> str:
    ruta = os.path.join(INPUT_DIR, filename)
    hash_md5 = hashlib.md5()
    with open(ruta, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def cargar_progreso(hash_fuente: str):
    if not os.path.exists(PROGRESS_FILE):
        return {"hash_fuente": hash_fuente, "ultimo_indice": 0, "chunk_actual": 1}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        progreso = json.load(f)
    if progreso.get("hash_fuente") != hash_fuente:
        logger.warning("La fuente cambió, reiniciando progreso")
        return {"hash_fuente": hash_fuente, "ultimo_indice": 0, "chunk_actual": 1}
    return progreso


def guardar_progreso(progreso: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progreso, f, indent=2)


def guardar_chunk(resultados: dict, chunk_num: int):
    if not resultados:
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.DataFrame.from_dict(resultados, orient="index")
    df["fechaScraping"] = pd.Timestamp.now()
    output_path = os.path.join(OUTPUT_DIR, f"rucs_chunk_{chunk_num}.xlsx")
    df.to_excel(output_path, engine="openpyxl")
    logger.info(f"Chunk {chunk_num} guardado: {output_path}")
