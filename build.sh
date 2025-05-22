#!/user/bin/env bash

set -oerrexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

