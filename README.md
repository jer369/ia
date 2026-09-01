# Portal Legislativo V2

Proyecto Flask para un asistente institucional y legislativo. Reemplaza la lógica de Pokémon del proyecto original por módulos de legislación, fiscalización, gestión, senadores, comunicación, trámites e institucionalidad.

## Requisitos
- Python 3.10+
- Ollama instalado si se quiere usar IA local.
- Modelo `llama3.2` descargado en Ollama.

## Instalación en Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
ollama pull llama3.2
python app.py
```

Abrir: http://127.0.0.1:5000

## API del propio sistema
- `GET /health`
- `GET /api/estadisticas`
- `GET /api/legislativo/buscar?q=proyectos`
- `POST /chat` con `{ "pregunta": "..." }`
- `POST /api/memoria/limpiar`

## Integración futura
Las fuentes externas deben conectarse en `services/legislativo.py` o mediante un cliente HTTP separado. Las claves deben permanecer en `.env`, nunca en JavaScript ni GitHub.
