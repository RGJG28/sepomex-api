import requests
import json
import chardet
from fastapi import FastAPI, HTTPException
from typing import List, Dict



TOKEN_DropBox = "sl.u.AGaZijH-k8_MpqutiwowqkQr_U0rnxZtcjh3K-U-lxVeFjv6VFk1E1tceQOWE1Sp-Q2ZGkhrU9rxH4gGRbh0PJhAKjCvIw8KYdk6Sz8Bpr_rkPzfTiN16VNlU4ljxjFH5kVcZkEt-zcFpi0v8dNbxEyFxUwJpY0A845WaBtIWoIG7WYdass32D83GwXmvJ-yqK9ih732WkoLKFUxz8nXNIEQ6q6Bp8jnDtoWDW1TFwb923vaIrYOrJumUgtf2sQDbiTZoI1Etw9uYCU2_mcIUFmjnLnVv9avHv8t6OYl-MKErGAX23LYB269WpX6pUBaUcOQekimWKAOqmo4MIpvO_PuF8_kHu6gg6viGY0OSrhdpk4FAwwxn39p32h4SjNJPnerueHwPUKaMBubq8f_fg3RB_SvG_vrZWafQYQNaDc22PdHQ7yJeN8kBFFIhKlKKv1hmekcZFe6IxvaC9tYmXvVpiS2mnmR86ogK-GuTlP_batC1MnoVjadAdUanx5PepAvzyADtOnpYXdm91uOjh4L1-oxvJYVU1jHBNyPDxIWQACIBE3a5D_XnkMmrv904xf0XUBGly65SkWQoPNWUXdSCyuW7GGnN9yIsyMJXKn3a-dZbYQziVGtjTL521RtJ9jEXS3DhGzEPc_me9jyiLHql076zGGDTn5I3KHeplYzsUqXfOxc9kQH2FONBTvsB7RyEpB82Ew7_1YGNVpSZGYnocNbAigzyK7WXYfyb7Y4nR4uEGlhDVft_dPgTAnrPQS_ByywQKBJnyGOLVYEanFYuXqyVg-eEsRGN8hY0riUQt2U0qxPqfGfFVV4xJYKxr5b8iMk53Dwe1sojVolqKZ0xIMMFS77gwPn2T8n8OfDv8AReGD1PfgHpZI-qYIjyCQ_BdTdoR0uowK6bFsTYvptaP58cjqGuy8i64kxJoMAxRKxZgPZV6LhiZRy8V9jsC91Ran0YW5JSBh8DjnaB6HApgzscpF8t9McwrdJePdDAuHUYRj52EY_Xzt_eqeOBc_ioRenLO4EOsow9kkjhx2sHvhEN-1CSeFCpqT-7AsW_rGleG54K6wC9zChfj2QlHr8hpITTlZys21aN4E_KddgvTYsNrcOkzVLoMQ2hHSS9n9-NX_dJwJrUdrH26ULYIi1kncs9KDHu0ABWTte58gEkLX6MyLp9qx_7irwn8YVMIaJUbsWutzjBr8OSlm7SHvnj7BPzQYUPpHnHYuTPne7cA5TUuWL2_hAnxqzwSajeco7NmrQ7qykY1qZoDU6LyLPDxjle3ZsoWbkocNRlEBJ"

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