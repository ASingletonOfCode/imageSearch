# Make target to run python manage.py runserver
# Usage: make runserver
runserver:
	python manage.py runserver

# Make target to run python manage.py test
# Usage: make test
test:
	python manage.py test

# Make target to run black formatter
# Usage: make black
black:
	black .