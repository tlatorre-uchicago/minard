#!/bin/sh

if ps -e | grep gunicorn; then
    exit 0
else
    cd /home/tlatorre/proj/sno+
    source bin/activate
    cd src/minard
    ./runserver.py
fi
