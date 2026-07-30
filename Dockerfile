FROM python:3.11-slim

# WeasyPrint system dependencies (Pango, Cairo, GDK-Pixbuf, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
        libcairo2 libffi-dev fonts-dejavu fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV DB_PATH=/srv/data/hrdocs.db
EXPOSE 5000
# Binds to the host-assigned port: Railway/Render $PORT, else Zoho Catalyst's
# variable, else 5000 (VPS/local). Works unchanged everywhere.
CMD ["sh","-c","gunicorn 'app:create_app()' -b 0.0.0.0:${PORT:-${X_ZOHO_CATALYST_LISTEN_PORT:-5000}} -w 2 --timeout 120"]
