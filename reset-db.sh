#!/bin/sh

rm ingenuity-dev.db 
rm -r migrations/
flask db init
flask db migrate
flask db upgrade
