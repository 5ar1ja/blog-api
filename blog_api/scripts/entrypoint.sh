#!/bin/bash
set -e

echo "============================================="
echo "Starting Blog API via Docker"
echo "============================================="

# Function to wait for Redis
wait_for_redis() {
    echo "Waiting for Redis to become available..."
    while ! curl -s "http://redis:6379" > /dev/null 2>&1 && ! python -c "import redis; r = redis.Redis(host='redis', port=6379); r.ping()" > /dev/null 2>&1; do
        sleep 1
    done
    echo "Redis is up and running!"
}

wait_for_redis

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Compiling translations..."
django-admin compilemessages || echo "Skipping translations compilation"

# If SEED_DB environment variable is set to true, seed the database
if [ "$SEED_DB" = "true" ]; then
    echo "Seeding test data..."
    python manage.py loaddata users_data || echo "Users data already seeded"
    python manage.py loaddata blog_data || echo "Blog data already seeded"
fi

echo "============================================="
echo "Setup completed!"
echo "============================================="

# Execute the main process (passed from docker-compose or CMD)
exec "$@"
