#!/usr/bin/env bash


pip install -r requirements.txt
export APP_SETTINGS="project.config.ProductionConfig"
python manage.py create_db
python manage.py db init
python manage.py db migrate
python manage.py create_municipality
python manage.py create_admin
python manage.py create_test_user
