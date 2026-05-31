FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .
RUN pip install uv && uv sync --frozen
COPY . .
CMD ["uv", "run", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
