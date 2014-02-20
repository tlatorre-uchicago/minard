#!/bin/bash

export VIRTUALENV=/home/tlatorre/proj/sno+

if ps -e | grep -v grep | grep gunicorn; then
    :
else
    cd $VIRTUALENV
    source bin/activate
    cd src/minard
    ./runserver.py
fi

if ps -ef | grep -v grep | grep workers.py; then
    :
else
    cd $VIRTUALENV
    source bin/activate
    cd src/minard
    python minard/workers.py
fi
