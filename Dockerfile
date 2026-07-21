FROM python:3.12-slim
WORKDIR /app
# 兼容旧根 Dockerfile：请改用 backend/Dockerfile 或 docker-compose
COPY backend/ /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
