# Imagem base Python
FROM python:3.11-slim

# Evitar prompts de instalação
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Atualiza e instala dependências de sistema
RUN apt-get update && \
    apt-get install -y ffmpeg git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Cria pastas necessárias
RUN mkdir -p /app/media /app/static

# Dá permissões apropriadas
RUN chmod -R 755 /app

# Expõe porta 8000
EXPOSE 8000

# Comando para iniciar o Gunicorn
CMD ["gunicorn", "transcritor_site.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
