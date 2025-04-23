#!/bin/bash

poetry install
poetry run python src/manage.py makemigrations
poetry run python src/manage.py migrate
poetry run python src/manage.py runserver 0.0.0.0:8000

