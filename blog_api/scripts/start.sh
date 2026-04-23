#!/usr/bin/env bash
set -e

echo "============================================="
echo "Starting script for advanced django project"
echo "============================================="
echo ""
echo "Checking env variables.."

ENV_FILE="settings/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found"
    echo "Please create it: cp .env.example .env"
    exit 1
fi

export $(grep -v '^#' $ENV_FILE | xargs)

REQUIRED_VARS=("BLOG_ENV_ID" "BLOG_SECRET_KEY" "BLOG_REDIS_URL")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Environment variable $var is missing or empty."
        exit 1
    fi
done
echo "Env variables OK"

echo ""
echo "Setting up virtual env"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Venv created"
else
    echo "Venv already exists"
fi

source venv/bin/activate
pip install -r requirments/base.txt
echo "Dependencies installed"

echo ""
echo "Running migrations"
python manage.py makemigrations
python manage.py migrate
echo "Migrations complete"

echo ""
echo "Collecting static files"
python manage.py collectstatic --noinput --clear > /dev/null 2>&1 || echo "Static files skipped"

echo ""
echo "Compiling translations"
if command -v msgfmt > /dev/null 2>&1; then
    python manage.py compilemessages > /dev/null 2>&1 || echo "compilemessages warning"
    echo "Translations compiled"
else
    echo "gettext not found, skipping translations"
fi

echo ""
echo "Creating superuser"
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@admin.com').exists():
    User.objects.create_superuser(
        email='admin@admin.com',
        password='admin123',
        first_name='Admin',
        last_name='Adminovich'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
EOF

echo ""
echo "Seeding test data.."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from apps.blog.models import Category, Tag, Post, Comment

User = get_user_model()

if Post.objects.exists():
    print('Test data already exists')
else:
    users = []
    for i in range(1, 6):
        user, _ = User.objects.get_or_create(
            email=f'user{i}@test.com',
            defaults={
                'first_name': f'User{i}',
                'last_name': 'Test'
            }
        )
        user.set_password('testtest123')
        user.save()
        users.append(user)

    cat1 = Category.objects.create(slug='tech', name_en='Technology', name_ru='Технологии', name_kk='Технологиялар')
    cat2 = Category.objects.create(slug='lifestyle', name_en='Lifestyle', name_ru='Образ жизни', name_kk='Өмір салты')
    cat3 = Category.objects.create(slug='news', name_en='News', name_ru='Новости', name_kk='Жаңалықтар')
    categories = [cat1, cat2, cat3]

    tag1 = Tag.objects.create(name='python', slug='python')
    tag2 = Tag.objects.create(name='django', slug='django')
    tag3 = Tag.objects.create(name='kbtu', slug='kbtu')
    tag4 = Tag.objects.create(name='news', slug='news')
    tag5 = Tag.objects.create(name='review', slug='review')
    tags = [tag1, tag2, tag3, tag4, tag5]

    for i in range(15):
        post = Post.objects.create(
            title=f'Post {i+1}',
            slug=f'post-{i+1}',
            body=f'This is the content of post {i+1} ' * 20,
            author=users[i % 5],
            category=categories[i % 3],
            status='published' if i % 4 != 0 else 'draft'
        )
        post.tags.set([tags[i % 5]])

    for post in Post.objects.all():
        for j in range(2):
            Comment.objects.create(
                post=post,
                author=users[j % 5],
                body=f'Comment {j+1} on {post.title}'
            )
    
    print('Test data created')
    print(' - 5 users')
    print(' - 3 categories')
    print(' - 5 tags')
    print(' - 15 posts')
    print(' - 30 comments')
EOF

echo ""
echo "Setup completed"
echo ""
echo "URLs:"
echo " API: http://127.0.0.1:8000/api/"
echo " ReDoc: http://127.0.0.1:8000/api/docs/redoc/"
echo " Swagger: http://127.0.0.1:8000/api/docs/swagger-ui/"
echo ""
echo "Superuser"
echo "Email: admin@admin.com"
echo "Password: admin123"
echo ""
echo "Test users"
echo " user1@test.com - user5@test.com"
echo " Password: testtest123"
echo ""

python manage.py runserver
