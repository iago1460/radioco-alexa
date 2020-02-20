#!/bin/sh

python3 manage.py migrate
python3 manage.py collectstatic --no-input

#exec uwsgi --socket 0.0.0.0:8000 --ini ./radioco.ini --master --processes 2 --threads 1
exec uwsgi --http-socket :8000 --workers=2 --offload-threads=2 --ini radioco.ini