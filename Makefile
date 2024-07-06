install:
	poetry install

build:
	./build.sh



dev:
	poetry run flask --app page_analyzer:app --debug run --port 8000

# poetry run flask --app example --debug run --port 8000


PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app


lint:
	poetry run flake8 page_analyzer tests

check:
	poetry run flake8 page_analyzer tests
	poetry run pytest -s

test-coverage:
	poetry run pytest --cov-report xml --cov=page_analyzer
