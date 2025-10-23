@echo off
setlocal

echo {"lingos": []} > db.json
echo "" > .env

python -m venv venv

call venv\Scripts\activate

python -m pip install -r requirements.txt

endlocal
