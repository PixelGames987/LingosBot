@echo off
setlocal

echo {"lingos": []} > db.json

python -m venv venv

call venv\Scripts\activate

python -m pip install -r requirements.txt

endlocal
