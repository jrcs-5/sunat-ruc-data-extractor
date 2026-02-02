import asyncio
from config.logging_config import setup_logging
from services.file_handler import *
from scraper.sunat_scraper import SunatRUCClient
import logging

ARCHIVO = "Registro de RUCs.xlsx"
CHUNK_SIZE = 100

setup_logging()
logger = logging.getLogger(__name__)


async def main():
    logger.info("Iniciando el scraper de SUNAT RUC")
    ruc_list = get_rucs(ARCHIVO, 'RUC')
    total = len(ruc_list)
    
    hash_fuente = calcular_hash_archivo(ARCHIVO)
    progreso = cargar_progreso(hash_fuente)
    inicio = progreso["ultimo_indice"]
    chunk_actual = progreso["chunk_actual"]
    
    logger.info(f"Reanudando desde índice: {inicio}")
    
    client = SunatRUCClient()
    await client.start()
    
    resultados_chunk = {}
    try:
        for i in range(inicio, total):
            ruc = ruc_list[i]
            logger.info(f"[{i + 1}/{total}] Consultando RUC: {ruc}")
            resultados_chunk[ruc] = await client.consultar_ruc(ruc)
            if len(resultados_chunk) == CHUNK_SIZE:
                guardar_chunk(resultados_chunk, chunk_actual)
                progreso["ultimo_indice"] = i + 1
                progreso["chunk_actual"] += 1
                guardar_progreso(progreso)
                resultados_chunk.clear()
                chunk_actual += 1
        if resultados_chunk:
            guardar_chunk(resultados_chunk, chunk_actual)
            progreso["ultimo_indice"] = total
            guardar_progreso(progreso)
    except KeyboardInterrupt:
        logger.warning("Ejecución pausada manualmente (Ctrl+C)")

    except Exception as e:
        logger.exception(f"Error fatal en main: {e}")
    finally:
        await client.close()
        logger.info("Browser cerrado")
        logger.info("Proceso finalizado")


if __name__ == "__main__":
    asyncio.run(main())