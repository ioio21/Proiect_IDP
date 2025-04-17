FROM python:3.10-slim
WORKDIR /backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8001

ENV PYTHONPATH=/backend/src

CMD ["uvicorn", "src.database:app", "--host", "0.0.0.0", "--port", "8001"]