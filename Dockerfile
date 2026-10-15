FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY sql ./sql
COPY scripts ./scripts

ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn","chatbi.api:app","--host","0.0.0.0","--port","8000"]
