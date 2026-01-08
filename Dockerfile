# ═══════════════════════════════════════════════════════════════════════════════
# VinciPitch.AI - Dockerfile para GCP Cloud Run
# ═══════════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (necessário para alguns pacotes Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta (GCP Cloud Run usa a variável PORT)
EXPOSE 8080

# Comando para executar a aplicação
# Cloud Run define a variável PORT automaticamente
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
