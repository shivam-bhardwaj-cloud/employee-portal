# --- PHASE 4 CHANGE: Base Image ---
# Phase 3 used 'alpine'. We switched to 'slim' (Debian) for better 
# compatibility with 'psycopg2' (Postgres driver).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# --- PHASE 4 CHANGE: Installation ---
# Removed 'apk add' (Alpine commands).
# Pip installs directly.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure logs appear immediately
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# --- PHASE 4 CHANGE: Production Server ---
# Phase 3 used: CMD ["python", "app.py"]
# Phase 4 uses: Gunicorn (Production WSGI Server) for better concurrency.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]