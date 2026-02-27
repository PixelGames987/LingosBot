#!/bin/bash

set -e

echo '{"lingos": []}' > db.json
if [ -e ".env" ]; then
	echo -e "\n.env already exists\n"
else
	echo -e "\nCreating an example .env file...\n"
	cat .env.example | tee .env
fi

echo -e "Creating python venv and installing dependencies...\n"
python -m venv venv
./venv/bin/python -m pip install -r requirements.txt
