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

## Env variables:
LESSON_COUNT - (int) Number of lessons to do per session

CHANCE_OF_PASSING - (float) Chance of the bot to be correct/incorrect. 1 - correct everytime, 3 - correct every 3 questions, etc.

EMAIL - (str) Your email

PASSWORD - (str) Your password

AUTOMATED_LOGIN - (0/1) Should the code log in by itself using the specified credentials?

HEADLESS - (0/1) Should the browser run in a headless mode? (without a window)

CLEAR_DB_BEFORE_SESSION - (0/1) Should the code remove all DB entries before every session?

FORCE_WAIT_SEC - (float) For debugging. How long should the code wait between actions
