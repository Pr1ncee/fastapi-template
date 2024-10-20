FROM python:3.12.6-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends curl gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --deploy --system --ignore-pipfile

COPY . /app/
COPY scripts/ ./scripts/

RUN chmod +x /app/scripts/entrypoint.sh
ENTRYPOINT ["/bin/bash", "scripts/entrypoint.sh"]
