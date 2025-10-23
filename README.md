# LingosBot
A bot for lingos.pl made with python and selenium

## Setup on Linux:
```
Install python, python-pip, python-venv, firefox

git clone https://github.com/PixelGames987/LingosBot
cd LingosBot
chmod +x setup.sh start.sh
./setup.sh

Copy the contents of .env.example into .env and set your email, password and other parameters

Run with ./start.sh
```

## Setup on Windows:
```
Install Python (newest), git and Firefox
Open cmd and go to the desktop

git clone https://github.com/PixelGames987/LingosBot
cd LingosBot
setup.bat

Copy the contents of .env.example into .env and set your email, password and other parameters

Run with start.bat
```

## Automated lessons:
To make the script fully automatic, edit the main.py file and add your credentials, change AUTOMATIC_LOGIN to 1 and set the number of lessons to do per run.
