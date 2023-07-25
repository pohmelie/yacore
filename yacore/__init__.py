# ruff: noqa
from importlib import resources

from cock import build_entrypoint, get_options_defaults, Config, Option
from facet import ServiceMixin

from yacore.injector import inject, register

__version__ = resources.files("yacore").joinpath("version.txt").read_text().strip()
version = tuple(map(int, __version__.split(".")))
