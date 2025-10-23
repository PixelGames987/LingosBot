#!/bin/bash

set -e

echo '{"lingos": []}' > db.json
touch .env

python -m venv venv
./venv/bin/python -m pip install -r requirements.txt
