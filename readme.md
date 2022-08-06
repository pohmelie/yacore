# yacore — **Y**et **A**nother **CORE** library

[![Github actions status for master branch](https://github.com/pohmelie/yacore/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/pohmelie/yacore/actions)
[![Codecov coverage for master branch](https://codecov.io/gh/pohmelie/yacore/branch/master/graph/badge.svg)](https://codecov.io/gh/pohmelie/yacore)
[![Pypi version](https://img.shields.io/pypi/v/yacore.svg)](https://pypi.org/project/yacore/)
[![Pypi downloads count](https://img.shields.io/pypi/dm/yacore)](https://pypi.org/project/yacore/)

# Reason
TBD

# Features
TBD

# Requirements
- python 3.9+

# Documentation
TBD

# License
`yacore` is offered under MIT license.

# Development
## Run tests
Since coverage issue/feature, plugins coverage is broken by default. [Workaround](https://pytest-cov.readthedocs.io/en/latest/plugins.html):
``` bash
COV_CORE_SOURCE=yacore COV_CORE_CONFIG=.coveragerc COV_CORE_DATAFILE=.coverage.eager pytest
```
