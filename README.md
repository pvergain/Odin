# Odin

Odin is the new Loki. LMS for HackSoft Academy

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)](https://github.com/pydanny/cookiecutter-django/)
[![Build Status](https://travis-ci.org/HackSoftware/Odin.svg?branch=master)](https://travis-ci.org/HackSoftware/Odin)

## Setup
Virtual environment with python 3.6.1

```bash
pip install -r requirements/local.txt
pip install -r requirements/test.txt
```

1. Setup environment variables for recaptcha and OAuth application
2. Create a shell script as utility/bootstrap.sh.sample with your username
3. Run bootstrap.sh

## Tests

To run tests:

```bash
$ py.test
```

To run the tests, check your test coverage, and generate an HTML coverage report:

```bash
$ coverage run manage.py test
$ coverage html
$ open htmlcov/index.html
```
