echo "Generating coverage report"
coverage run --source='.' manage.py test && coverage html