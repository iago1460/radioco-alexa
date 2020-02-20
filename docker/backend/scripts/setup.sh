#!/bin/bash -x

python3 /srv/radioco/backend/manage.py migrate
#python3 /srv/radioco/backend/manage.py search_index --reindex -f
