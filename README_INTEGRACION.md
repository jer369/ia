# Arquitectura Portal Legislativo + Página Express

## Arquitectura final

- `portal_legislativo/`: backend, IA, datos institucionales y API.
- `pagina-express/`: página externa Node.js + Express.
- `portal_legislativo/static/chat-embed.js`: único widget embebible.

La Página Express **no copia el backend**. Solo carga:

```html
<script src="http://127.0.0.1:5000/static/chat-embed.js"
        api-url="http://127.0.0.1:5000/api/chat"></script>
```

En producción se cambia `127.0.0.1:5000` por el dominio HTTPS del Portal Legislativo.

## Comunicación

```text
Navegador
   |
   | carga script
   v
Página Express :3000
   |
   | chat-embed.js
   v
Portal Legislativo :5000
   |
   +--> POST /api/chat
   +--> GET  /health
   +--> GET  /api/legislativo/buscar
   +--> POST /api/tramite
   +--> POST /api/memoria/limpiar
   |
   +--> Ollama / datos / servicios institucionales
```

## Por qué el session_id viaja en JSON

No se depende de cookies de Flask entre dominios. El widget crea un `session_id` y lo envía en cada petición. Esto hace que el historial sea independiente de que Express y Portal estén en servidores diferentes.

## Ejecutar local

### 1. Portal Legislativo

```powershell
cd portal_legislativo
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Debe responder:

`http://127.0.0.1:5000/health`

### 2. Página Express

En otra terminal:

```powershell
cd pagina-express
npm install
npm start
```

Abrir:

`http://localhost:3000`

## Cambio a producción

En `pagina-express/public/index.html` cambia:

```html
src="http://127.0.0.1:5000/static/chat-embed.js"
api-url="http://127.0.0.1:5000/api/chat"
```

por:

```html
src="https://portal-legislativo.TU-DOMINIO.bo/static/chat-embed.js"
api-url="https://portal-legislativo.TU-DOMINIO.bo/api/chat"
```

También cambia los cuatro `avatar` y `tracking-url` si corresponde.

En `portal_legislativo/.env` cambia:

```env
ALLOWED_ORIGINS=https://pagina-express.TU-DOMINIO.bo
FLASK_DEBUG=false
```

## Importante

Para producción se recomienda HTTPS en ambos sitios. No se debe publicar `FLASK_SECRET_KEY` ni las claves de APIs.
