# ruff: noqa
from importlib import resources

from cock import build_entrypoint, get_options_defaults, Config, Option
from facet import ServiceMixin

from yacore.injector import inject, register

__version__ = resources.read_text("yacore", "version.txt").strip()
version = tuple(map(int, __version__.split(".")))
