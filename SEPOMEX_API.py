import requests
import json
import chardet
from fastapi import FastAPI, HTTPException
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN_DropBox = os.getenv("TOKEN_DROPBOX")
if not TOKEN_DropBox:
    raise Exception("Falta TOKEN_DROPBOX en variables de entorno")

app = FastAPI()

def leer_archivo(path):
    r = requests.post(
        "https://content.dropboxapi.com/2/files/download",
        headers={
            "Authorization": f"Bearer {TOKEN_DropBox}",
            "Dropbox-API-Arg": json.dumps({
                "path": path
            })
        }
    )

    if r.status_code == 200:
        encoding = chardet.detect(r.content)
        #print(encoding)
        return r.content.decode("latin-1")
    else:
        print(r.text)
        return None

# uso
contenido = leer_archivo("/CPdescarga.txt")
DATA = contenido
# ====== PARSER ======
def parse_data(text: str):
    lines = text.strip().split("\n")
    
    headers = lines[1].split("|")
    data_lines = lines[2:]
    
    cp_map = {}
    estado_map = {}
    colonia_map = {}
    estado_clave_map = {}  # 👈 NUEVO

    for line in data_lines:
        values = line.split("|")
        row = dict(zip(headers, values))

        cp = row["d_codigo"]
        colonia = row["d_asenta"]
        estado = row["d_estado"]
        ciudad = row["d_ciudad"] or None
        clave_estado = row["c_estado"]

        # ===== NUEVO: mapa estado → clave =====
        estado_clave_map[estado] = clave_estado

        # ===== Agrupar por CP =====
        if cp not in cp_map:
            cp_map[cp] = {
                "codigo_postal": cp,
                "estado": estado,
                "ciudad": ciudad,
                "colonias": []
            }
        cp_map[cp]["colonias"].append(colonia)

        estado_map.setdefault(estado.lower(), set()).add(cp)
        colonia_map.setdefault(colonia.lower(), set()).add(cp)

    estado_map = {k: list(v) for k, v in estado_map.items()}
    colonia_map = {k: list(v) for k, v in colonia_map.items()}

    return cp_map, estado_map, colonia_map, estado_clave_map

# ASIGNACION GLOBAL
cp_map, estado_map, colonia_map, estado_clave_map = parse_data(DATA)

# ====== ENDPOINTS ======

@app.get("/cp/{codigo_postal}")
def get_cp(codigo_postal: str):
    result = cp_map.get(codigo_postal)
    if not result:
        raise HTTPException(status_code=404, detail="Código postal no encontrado")
    return result


@app.get("/estado/{estado}")
def get_by_estado(estado: str):
    cps = estado_map.get(estado.lower())
    if not cps:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    
    return [cp_map[cp] for cp in cps]

@app.get("/estados")
def get_estados():
    return {
        "estado_clave": dict(sorted(estado_clave_map.items()))
    }

@app.get("/estado-clave/{clave}")
def get_estado_por_clave(clave: str):
    for estado, c in estado_clave_map.items():
        if c == clave:
            return {"estado": estado, "clave": clave}
    raise HTTPException(status_code=404, detail="Clave no encontrada")

@app.get("/colonia/{nombre}")
def get_by_colonia(nombre: str):
    nombre = nombre.lower()
    
    matches = [
        cp for col, cps in colonia_map.items()
        if nombre in col
        for cp in cps
    ]

    if not matches:
        raise HTTPException(status_code=404, detail="Colonia no encontrada")

    return [cp_map[cp] for cp in set(matches)]