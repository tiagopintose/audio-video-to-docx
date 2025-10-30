# Imagem base Python
FROM python:3.11-slim

# Evitar prompts de instalação
ENV DEBIAN_FRONTEND=noninteractive

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

# Cria pasta media
RUN mkdir -p /app/media

# Expõe porta 8000
EXPOSE 8000

# Comando para iniciar o Django
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
