FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies (Flask, Boto3, Gunicorn)
# --no-cache-dir tells pip: "Don't save the downloaded files", saving space.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure logs appear immediately
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Start the production server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
