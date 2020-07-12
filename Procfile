release: python manage.py makemigrations --no-input
release: python manage.py migrate --no-input

web: gunicorn ontrack.wsgi:application --preload --log-file - 