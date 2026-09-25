# ---------- Base ----------
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# ---------- Test image ----------
FROM base AS test
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
CMD ["pytest", "--cov=app", "--cov-report=xml", "--cov-report=term", \
     "--junitxml=reports/junit.xml"]

# ---------- Production image ----------
FROM base AS production
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd -m appuser
COPY app ./app
COPY templates ./templates
COPY static ./static
COPY wsgi.py ./
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:3000/health')" || exit 1
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:3000", "wsgi:app"]
