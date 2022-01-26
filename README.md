<div align="center">
    <img src=".github/images/astrobot.png" alt="astrobot readme image">

The all-encompassing, god-level bot for mochjicord.

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/dev/peps/pep-0020/#the-zen-of-python)
[![code-size](https://img.shields.io/github/languages/code-size/astro-devel/astrobot)](#)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a298c9e39bcb4428a033f25d02f0d4b4)](https://www.codacy.com/gh/astro-devel/astrobot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=astro-devel/astrobot&amp;utm_campaign=Badge_Grade)
[![docker-workflow](https://github.com/astro-devel/astrobot/actions/workflows/docker-image.yml/badge.svg?branch=master&event=push)](https://github.com/astro-devel/astrobot/actions/workflows/docker-image.yml)
[![license-mit](https://img.shields.io/github/license/astro-devel/astrobot)](https://github.com/astro-devel/astrobot/blob/master/LICENSE)
[![github-issues](https://img.shields.io/github/issues/astro-devel/astrobot)](https://github.com/astro-devel/astrobot/issues)
[![github-pull-requests](https://img.shields.io/github/issues-pr/astro-devel/astrobot)](https://github.com/astro-devel/astrobot/pulls)

</div>

# Environment
Astrobot uses multiple environment variables so that things like secret tokens and database credentials are not hardcoded into the codebase. These variables are managed with [python-dotenv](https://pypi.org/project/python-dotenv/), which takes these variables from a '.env' file located in the root directory of the project. A template of this file can be found in [templates/.env.default](https://github.com/astro-devel/astrobot/blob/master/templates/.env.default).

# Building & running
The bot can be run either locally, or in docker. We recommend managing dependencies with [Poetry](https://python-poetry.org/), but they can be installed with pip (preferably inside of a [virtualenv](https://virtualenv.pypa.io/en/latest/)). In order to set up the environment, and run the bot, run the following commands:
```
# using Poetry

poetry install
poetry shell

# using virtualenv

python3 -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

# set up environment variables

source mochji.env

# running the bot

python3 -m astrobot.bot
```

# Contributing
TBA

# Links
TBA