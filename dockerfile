FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code from your local project
COPY . .

# Expose the port 1081 in the docker container
EXPOSE 1081

# start command to initialize the FastApI app
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1081"]