# 📮 SEPOMEX API - México Postal Code Service

API REST desarrollada en Python con FastAPI para consultar el catálogo de códigos postales de México (SEPOMEX).  
Procesa datos en memoria desde un archivo plano optimizando velocidad de búsqueda sin necesidad de base de datos.

---

## 🚀 Características

- Consulta por código postal (CP)
- Búsqueda por estado
- Búsqueda parcial por colonia
- Agrupación automática de colonias por CP
- Procesamiento en memoria (alto rendimiento)
- Datos oficiales de SEPOMEX
- Preparada para despliegue en la nube

---

## 🛠 Tecnologías

- Python 3.10+
- FastAPI
- Uvicorn
- Requests
- Chardet
- Python-dotenv

---

## 📦 Instalación

```bash
git clone https://github.com/tu-usuario/sepomex-api.git
cd sepomex-api
pip install -r requirements.txt
```

## ▶️ Ejecución local
```bash
uvicorn SEPOMEX_API:app --reload
```
Abrir en navegador:
```bash
http://127.0.0.1:8000/docs
```
🔐 Variables de entorno

Crear archivo .env en la raíz del proyecto:
```bash
TOKEN_DROPBOX=tu_token_aqui
```

🌐 Endpoints
📍 Obtener por código postal
```
GET /cp/{codigo_postal}
```
Ejemplo:
```
/cp/01000
```
🏙️ Obtener por estado
```
GET /estado/{estado}
```
Ejemplo:
```
/estado/Ciudad de México
```
🏘️ Buscar por colonia
```
GET /colonia/{nombre}
```
Ejemplo:
```
/colonia/alpes
📤 Ejemplo de respuesta
{
  "codigo_postal": "01000",
  "estado": "Ciudad de México",
  "ciudad": "Ciudad de México",
  "colonias": [
    "San Ángel"
  ]
}
```

---

⚙️ Arquitectura
Parsing del archivo SEPOMEX en memoria al iniciar la API
Índices optimizados:
- cp_map → acceso directo por código postal
- estado_map → búsqueda por estado
- colonia_map → búsqueda parcial por colonia

---
☁️ Despliegue
Compatible con:
- Render
- Railway
- Fly.io
- VPS Linux
- Docker
---
Comando de producción:
```
uvicorn SEPOMEX_API:app --host 0.0.0.0 --port 10000
```

📌 Autor
Rodrigo G. Jimenez G.  
Proyecto backend con Python + FastAPI
