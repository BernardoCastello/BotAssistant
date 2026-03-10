FROM python:3.12-slim

WORKDIR /app

# Instala dependências primeiro (cache de layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Cria __init__.py necessários
RUN find src -type d -exec touch {}/__init__.py \;

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
