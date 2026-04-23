FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gettext \
    libpq-dev \
    gcc \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install python dependencies
COPY blog_api/requirments/base.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Add flower for monitoring celery
RUN pip install flower

# Copy project
COPY blog_api/ /app/

# Copy and set up entrypoint script
COPY blog_api/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
