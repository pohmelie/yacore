# 0.4.0 (27-07-2023)
- remove all `is_flag` options, since they conflict with `cock` library getting options from file
- `net.http.server`: `healthcheck` endpoint is disabled by default

# 0.3.2 (25-07-2023)
- add default to `is_flag=True` options to allow it in `get_options_defaults` result
- add option to disable healthcheck endpoint in `net.http.server`

# 0.3.1 (25-07-2023)
- fix `importlib.resources` deprication warning

# 0.3.0 (24-07-2023)
- add top-level imports from 3rd party libraries

# 0.2.0 (22-07-2023)
- target python version changed to `>= 3.11`
- log/loguru: fix `InterceptHandler` for python 3.11
- dev: use `ruff` linter instead of `flake8`

# 0.1.3 (08-01-2023)
- net.http.server: add new fastapi feature to use type annotation instead of a `response_model` argument
- ci: add python 3.11

# 0.1.2 (22-12-2022)
- update requirements minimal versions

# 0.1.1 (04-11-2022)
- db/postgresql: fix resource manipulation bug in migrator (#1)

# 0.1.0 (06-08-2022)
- initial implementation
