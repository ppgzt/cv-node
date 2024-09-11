#!/bin/sh
export FLASK_APP=./app/index.py
flask --debug run -h 0.0.0.0