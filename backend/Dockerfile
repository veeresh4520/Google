FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy and install dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8080

# Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
