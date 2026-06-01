# Workout API

API em FastAPI com MongoDB.

## Requisitos

- Python 3.12+
- (Opcional) Docker + Docker Compose

## Configuração

Crie o arquivo `.env` a partir do exemplo:

```bash
# Linux/macOS
cp infrastructure/.example.env infrastructure/.env
```

```powershell
# Windows (PowerShell)
Copy-Item infrastructure/.example.env infrastructure/.env
```

Variáveis esperadas:

- `MONGO_URI`
- `MONGO_DB_NAME`
- `JWT_SECRET`
- `JWT_EXPIRE_MINUTES`

Se for rodar fora do Docker, ajuste `MONGO_URI` para `mongodb://localhost:27017`.

## Rodando com Docker

```bash
cd infrastructure
docker compose up --build
```

API: http://localhost:8000

## Seeds (popular o banco)

A pasta `test/` fica na raiz do projeto e não é montada no container por padrão, por isso é necessário montá-la explicitamente:

```bash
# A partir de infrastructure/
docker compose run --rm -v ../test:/app/test:z workout-api uv run python -m test.seeds.seed
```

## Endpoints

### Geral
- `GET /health` → status da API
- `GET /docs` → Swagger UI
- `GET /openapi.json` → OpenAPI

### Workouts
- `POST /api/workouts/` → criar workout
- `GET /api/workouts/` → listar workouts
- `GET /api/workouts/{workout_id}` → buscar workout por ID
- `PATCH /api/workouts/{workout_id}` → atualizar workout
- `DELETE /api/workouts/{workout_id}` → remover workout

### Training Plans
- `POST /api/training-plans/` → criar plano de treino
- `GET /api/training-plans/` → listar planos de treino
- `GET /api/training-plans/{plan_id}` → buscar plano por ID
- `PATCH /api/training-plans/{plan_id}` → atualizar plano
- `DELETE /api/training-plans/{plan_id}` → remover plano


## Testando com Bruno

O repositório inclui uma collection do [Bruno](https://www.usebruno.com/) em `test/collection/` com requisições prontas para todos os endpoints.

Para usar:
1. Instale o Bruno em [usebruno.com](https://www.usebruno.com/)
2. Abra o Bruno e clique em **Open Collection**
3. Selecione a pasta `test/collection/`
4. Execute as requisições com a API rodando em `http://localhost:8000`

## Referências

- [Trabalho da Segunda Unidade — API REST com MongoDB](https://gustavoleitao.notion.site/Trabalho-da-Segunda-Unidade-API-REST-com-MongoDB-3599da677dce80769fe6e6f189eb735e)
