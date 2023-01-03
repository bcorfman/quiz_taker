# quiz_taker

[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=274804850&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=EastUs)

Asks the user a series of multiple choice questions by topic area, and keeps track of progress.

This is a Python script with a console GUI (using npyscreen).

Quizzes are stored in JSON format.

I used this program extensively for my Security+ certification exam in 2020.

## Prerequisites

* Click on the *Open with GitHub Codespaces* badge above to launch the project in a browser or on your desktop inside Visual Studio Code.

OR

* Install [Python](https://www.python.org) 3.8.1 or higher
* Install [Poetry](https://python-poetry.org)
* At a command prompt in the project directory, type `poetry install` to set up dependencies

## To run the code

* In the terminal window, type `poetry run python quiz.py`.

## Console GUI Controls

* Cursor up/down to highlight a choice, and SPACE or ENTER to select it.
* TAB to the Confirm button, and then SPACE or ENTER to confirm the selection.
* Continue through all the questions and receive a final score, or hit ESC to quit early and receive a score up that point.
