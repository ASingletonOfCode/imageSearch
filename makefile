# Make target to run python manage.py runserver
# Usage: make runserver
runserver:
	python manage.py runserver

# Make target to run python manage.py test
# Usage: make test
test:
	python manage.py test

# Make target to run tests with code coverage and then generate an HTML report in the htmlcov directory
# Usage: make coverage
coverage:
	coverage run --source='.' manage.py test && coverage html


# Make target to run black formatter
# Usage: make black
black:
	black .

# Update the requirements.txt file from pip
update_requirements:
	pip freeze > requirements.txt	

# Make target to start the django shell
# Usage: make shell
shell:
	python manage.py shell

# Make target to build the docker image
# Usage: make build
build:
	docker build -t image-search .

# Make target to run the docker container in detached
# Usage: make run
run:
	docker run -d --name imageSearch -p 8000:8000 image-search

# Make target to build then run a new docker image
# Usage: make docker_run
docker_run: 
	if docker container ls | grep imageSearch; then docker stop imageSearch && docker rm imageSearch; fi
	make build
	make run