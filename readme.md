<p align="center">
  <img width="350" height="350" src="https://raw.githubusercontent.com/pohmelie/yacore/master/docs/img/yacore.png" alt="yacore">
</p>
<h1 align="center" style="font-size: 3rem; margin: -15px 0">yacore</h1>

---

<div align="center">
<p>

<a href=https://github.com/pohmelie/yacore/actions>
  <img src="https://github.com/pohmelie/yacore/actions/workflows/ci.yml/badge.svg?branch=master" alt="Github actions status for master branch">
</a>
<a href=https://codecov.io/gh/pohmelie/yacore>
  <img src="https://codecov.io/gh/pohmelie/yacore/branch/master/graph/badge.svg" alt="Codecov coverage for master branch">
</a>
<a href=https://pypi.org/project/yacore>
  <img src="https://img.shields.io/pypi/v/yacore.svg" alt="Pypi version">
</a>
<a href=https://pypi.org/project/yacore>
  <img src="https://img.shields.io/pypi/dm/yacore" alt="Pypi downloads count">
</a>

</p>

<strong>Y</strong>et <strong>A</strong>nother <strong>CORE</strong> library

</div>

---

`yacore` is a set of service-like «backends» to build your application on top of.

## Reason

- Reduce daily routine to start new service.
- Reduce errors on copy/paste things from previous projects.

## Features

- Build on top of [`facet`](https://github.com/pohmelie/facet), [`cock`](https://github.com/pohmelie/cock) and [`giveme`](https://github.com/steinitzu/giveme). This means **services**, **configuration** and **dependency injection**.
- Flexible installation (install only what you need for current service, e.g. `pip install yacore[db.postgresql,net.http]`)
- Couple backends for databases, logging, networking and whatever in strict service-like style.

See [docs](https://pohmelie.github.io/yacore) for more details.

## Requirements

- python 3.9+

## Usage

You can start new project from scratch with cookiecutter template via:

```
cookiecutter gh:pohmelie/cookiecutter-yacore
```

Read more at [cookiecutter-yacore](https://github.com/pohmelie/cookiecutter-yacore).

## Documentation

TBD

## License

`yacore` is offered under MIT license.

## Development

### Installation

```bash
pip install -e ./[dev]
```

### Run tests

Since coverage issue/feature, plugins coverage is broken by default. [Workaround](https://pytest-cov.readthedocs.io/en/latest/plugins.html):

```bash
COV_CORE_SOURCE=yacore COV_CORE_CONFIG=.coveragerc COV_CORE_DATAFILE=.coverage.eager pytest
```