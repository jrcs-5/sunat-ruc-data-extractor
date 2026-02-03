# 🧾 sunat-ruc-data-extractor

Herramienta en **Python** para **extraer datos públicos de SUNAT a partir de RUCs**, leyendo desde Excel, procesando de forma secuencial y guardando resultados en **chunks** con control de progreso.

Proyecto orientado a **automatización** y **scraping responsable**.

---

## ✨ Características

- Lectura de RUCs desde archivo **Excel**
- Scraping **secuencial** para evitar sobrecargar el portal SUNAT
- Exportación de resultados en archivos **Excel por chunks**
- Reanudación automática mediante archivo de progreso
- Detección de cambios en la fuente usando **hash MD5**
- Manejo de errores y **logging** integrado

---

## ⚖️ Uso responsable

Este proyecto consume únicamente **información pública** disponible en el portal de SUNAT.

Está pensado para fines **personales, educativos y técnicos**.  
El uso indebido o malicioso es responsabilidad del usuario.

---

## 🔁 Funcionamiento general

1. Se leen los RUCs desde un archivo Excel.
2. Se calcula un **hash MD5** del archivo fuente.
3. Si el archivo no ha cambiado, el proceso continúa desde el último RUC procesado.
4. Los resultados se guardan en **chunks configurables**.
5. El progreso se persiste en un archivo JSON interno.

> Si el archivo Excel cambia, el progreso se reinicia automáticamente.

---

## ⚙️ Configuración básica

En `main.py`:

```python
ARCHIVO = "Registro de RUCs.xlsx"
CHUNK_SIZE = 100
```
- El nombre del archivo puede cambiarse libremente.
- El tamaño del chunk es totalmente configurable.
- El navegador se define al inicializar el cliente.

## 🚀 Instalación y ejecución (Windows)
```bash
git clone https://github.com/tu-usuario/sunat-ruc-data-extractor.git

cd sunat-ruc-data-extractor

python -m venv venv

venv\Scripts\Activate.ps1

pip install -r requirements.txt

python main.py
```



## 🛠️ Notas técnicas

- El scraping es secuencial por diseño, pero la arquitectura permite adaptarlo fácilmente a ejecución paralela controlada.
- El archivo progress.json es interno y no debe modificarse manualmente.
- El proyecto está pensado para ejecutarse en Windows.
