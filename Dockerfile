FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv pip install --system . 

COPY main.py .

EXPOSE 8000

CMD ["python3", "main.py"]