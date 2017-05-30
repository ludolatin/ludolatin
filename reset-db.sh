#!/bin/sh

# rm ingenuity-dev.db
rm -r migrations/
flask db init
flask db migrate
flask db upgrade
python manage.py load_data
python manage.py add_admin
python manage.py load_products
