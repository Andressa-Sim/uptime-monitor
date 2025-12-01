# 1. Imagem base: Usa uma versão leve do Python
FROM python:3.9-slim

# 2. Define a pasta de trabalho dentro do container
WORKDIR /app

# 3. Copia os arquivos de requisitos primeiro (para aproveitar o cache)
COPY requirements.txt .

# 4. Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o restante do código do projeto
COPY . .

# 6. Informa ao Docker que a aplicação roda na porta 5000
EXPOSE 5000

# 7. Comando para iniciar a aplicação
CMD ["python", "app.py"]