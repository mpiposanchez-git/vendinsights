# Simple Dockerfile for mps_package API

FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy package sources
COPY . /app

# expose port for API
EXPOSE 8000

# run FastAPI app
CMD ["uvicorn", "mps_package.api:app", "--host", "0.0.0.0", "--port", "8000"]
