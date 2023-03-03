## Deploy template and answer configurator questions with cookiecutter.

```bash
pip install cookiecutter
cookiecutter gh:pohmelie/cookiecutter-yacore
```

## Modify dependencies

Add extra dependencies to `requirements/production.in` and `requirements/dev.txt`.

As for `yacore` itself, you can install only what you need for current service, just change plain `yacore` to something like `yacore[db.postgresql,net.http]` in `requirements/production.in` file.

**See [backends](backends.md) for more details.**

Compile `.in` dependencies to pin them.

```bash
cd your-project-name
pip install pip-tools
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
