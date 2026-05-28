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

## Seeds (popular o banco)

Com os containers já rodando:

```bash
docker compose exec api uv run python -m seeds.seed
```

## Rodando local (uv)

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Para rodar seeds localmente:

```bash
uv run python -m seeds.seed
```

## Endpoints

- `GET /health` → status da API
- `GET /docs` → Swagger UI
- `GET /openapi.json` → OpenAPI

## Referências

- [Trabalho da Segunda Unidade — API REST com MongoDB](https://gustavoleitao.notion.site/Trabalho-da-Segunda-Unidade-API-REST-com-MongoDB-3599da677dce80769fe6e6f189eb735e)
