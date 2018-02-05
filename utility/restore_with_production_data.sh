#!/bin/bash

USERNAME="radorado"

echo "Fetching latest dump ...\n"
curl -o db.dump `heroku pg:backups public-url --app odin-production`

echo "Recreating database ...\n"
dropdb --if-exists odin
sudo -u postgres createdb -O $USERNAME odin

echo "Starting pg_restore ...\n"
pg_restore -U $USERNAME -d odin -c -j 4 db.dump &> pg_restore_log
rm db.dump

echo "Migrations and data ...\n"
python manage.py migrate
