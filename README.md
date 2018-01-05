# Odin

Odin is the new Loki. LMS for HackSoft Academy

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)](https://github.com/pydanny/cookiecutter-django/)
[![Build Status](https://travis-ci.org/HackSoftware/Odin.svg?branch=master)](https://travis-ci.org/HackSoftware/Odin)
[![Coverage Status](https://coveralls.io/repos/github/HackSoftware/Odin/badge.svg?branch=master)](https://coveralls.io/github/HackSoftware/Odin?branch=master)

## Setup

### Virtual environment with python 3.6.1

* Install from here https://github.com/pyenv/pyenv-installer

* Export:
```
export PATH="/path.to.user/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
* Do `pyenv install 3.6.1`

* Create virtualenv with python3.6.1: `virtualenv -p ~/.pyenv/versions/3.6.1/bin/python3 odin`

### Install requirements

```bash
pip install -r requirements/local.txt
pip install -r requirements/test.txt
```

1. Setup environment variables for recaptcha and OAuth application
2. Create a shell script as utility/bootstrap.sh.sample with your username
3. Run bootstrap.sh

### Install JS requirements

```
npm install
```

* This installs bower and runs webpack as well as postinstall script.

## Celery

* Run celery with the following command `celery -A odin worker -l info`

## Tests

To run tests:

```bash
$ py.test
```

To run the tests and check your test coverage

```bash
$ py.test --cov=odin
```

## Grader

* Check this repository for reference -> https://github.com/HackSoftware/HackGrader
