# exit on error

# set -o errexit

# python manage.py collectstatic --no-input

python main.py migrate

python main.py runserver
