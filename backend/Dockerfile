FROM python:3.12-slim

WORKDIR /app

# Dependências de sistema (pdfplumber precisa de algumas libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Diretórios para endpoints legados
RUN mkdir -p uploads output

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
