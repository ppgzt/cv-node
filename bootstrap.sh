#!/bin/bash
# dir="/$1"

# if [ "$#" -eq "0" ] 
#   then
#     dir=$(pwd)
# fi
# export FLASK_APP="$dir/app/index.py"

# source "$dir/venv/bin/activate"
# # exec "$@"

# flask --debug run -h 0.0.0.0

export FLASK_APP=./app/index.py
pipenv run flask --debug run -h 0.0.0.0
