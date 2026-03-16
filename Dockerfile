#syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    libsqlite3-dev \
  && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8501
CMD ["streamlit", "run", "ui/app.py"]
