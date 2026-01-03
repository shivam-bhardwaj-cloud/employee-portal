# -------- builder stage --------
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --target /deps

COPY . .

# -------- runtime stage --------
FROM python:3.12-alpine

WORKDIR /app

# copy application
COPY --from=builder /app /app

# copy dependencies
COPY --from=builder /deps /deps

# make deps visible to python
ENV PYTHONPATH=/deps

# Expose the port
EXPOSE 5000

# IMPORTANT: exact python binary path
CMD ["python", "app.py"]
