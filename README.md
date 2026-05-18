# Workout API

API em FastAPI com MongoDB.

## Requisitos

- Python 3.12+
- (Opcional) Docker + Docker Compose

## Configuração

Crie o arquivo `.env` a partir do exemplo:

```bash
# Linux/macOS
cp .env.example .env
```

```powershell
# Windows (PowerShell)
Copy-Item .env.example .env
```

Variáveis esperadas:

- `MONGO_URI`
- `MONGO_DB_NAME`
- `JWT_SECRET`
- `JWT_EXPIRE_MINUTES`

Se for rodar fora do Docker, ajuste `MONGO_URI` para `mongodb://localhost:27017`.

## Rodando com Docker

```bash
docker compose up --build
```

API: http://localhost:8000

## Rodando local (uv)

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /health` → status da API
- `GET /docs` → Swagger UI
- `GET /openapi.json` → OpenAPI
