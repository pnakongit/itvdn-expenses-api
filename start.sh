#! /bin/sh

flask db upgrade

gunicorn -w 4 -k gevent --bind 0.0.0.0:$PORT 'app:create_app()' --log-level debug --reload
