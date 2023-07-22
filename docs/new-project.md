# Create new project

## Deploy template and answer configurator questions with cookiecutter.

```bash
pip install cookiecutter
```

```bash
cookiecutter gh:pohmelie/cookiecutter-yacore
```

## Modify dependencies

Add extra dependencies to `requirements/production.in` and `requirements/dev.txt`.

As for `yacore` itself, you can install only what you need for current service, just change plain `yacore` to something like `yacore[db.postgresql,net.http]` in `requirements/production.in` file.

**See [backends](backends.md) for more details.**

Compile `.in` dependencies to pin them.

```bash
cd your-project-name
```

```bash
pip install pip-tools
```

```bash
pii-compile requirements/production.in -o requirements/production.txt
```

## Install app

```bash
pip install -e ./[dev]
```

## Run app

```bash
python -m your-project-name
```

## Run tests

```bash
pytest
```

## Build docker image

```bash
docker build . -t my-app
```

# Project structure

Initial project structure tree looks like this:

```
new-project/
├── .github
│   └── workflows
│       └── new-project-ci.yml
├── new_project
│   ├── __init__.py
│   ├── __main__.py
│   ├── service.py
│   └── version.txt
├── requirements
│   ├── dev.txt
│   ├── production.in
│   └── production.txt
├── tests
│   └── conftest.py
├── .coveragerc
├── Dockerfile
├── .dockerignore
├── .flake8
├── .gitignore
├── pytest.ini
├── readme.md
└── setup.py
```

Lets walk through it.

## .github

Contains github actions workflows. In this case it is only one workflow for CI. CI consists of 2 steps: lint and test.

## new_project

Naming depends on what you answered in cookiecutter configurator.

Contains service source code. As you can see, it is a simple python package with `__init__.py` and `__main__.py` files. `__init__.py` contains version information and `__main__.py` contains code that starts service. `service.py` contains service code. `version.txt` contains service version.

## requirements

Contains requirements files. `production.in` contains requirements for production. `production.txt` contains pinned requirements for production. `dev.txt` contains requirements for development.

## tests

Contains tests. `conftest.py` contains pytest fixtures and configuration.

---

You can explore other parts of this project on your own, since they are pretty standard and straitforward.
