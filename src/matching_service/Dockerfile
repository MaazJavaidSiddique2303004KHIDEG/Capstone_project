FROM python:3.11-slim

RUN mkdir /src
RUN mkdir /src/matching_service
RUN touch /src/__init__.py
COPY . /src/matching_service

COPY requirements.txt .

RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Run the FastAPI application when the container starts
CMD ["uvicorn", "src.matching_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
