FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv
RUN addgroup --system django && adduser --system --ingroup django django && chown django:django /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY --chown=django:django . .
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
USER django

CMD ["/app/entrypoint.sh"]
