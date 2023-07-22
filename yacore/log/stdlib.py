import collections
import copy
import itertools
import logging
import logging.config
from pathlib import Path

import yaml
from click import Choice
from click import Path as ClickPath
from cock import Option, build_options_from_dict

from yacore.injector import inject

log_options = build_options_from_dict({
    "log-level": Option(default="debug", type=Choice(["debug", "info", "warning", "error"])),
    "log-config": Option(default=None, type=ClickPath(exists=True, dir_okay=False))
})


def deep_merge(target, *args, allow_none=False):
    if len(args) != 1:
        for obj in args:
            target = deep_merge(target, obj, allow_none=allow_none)
        return target

    source = args[0]

    if isinstance(source, collections.abc.Mapping):
        if isinstance(target, collections.abc.MutableMapping):
            for k, v in source.items():
                if k in target:
                    target[k] = deep_merge(target[k], v, allow_none=allow_none)
                else:
                    target[k] = copy.deepcopy(v)
        elif isinstance(target, collections.abc.Mapping):
            return dict(itertools.chain(target.items(), source.items()))
        else:
            return copy.deepcopy(source)
    elif isinstance(source, collections.abc.Set):
        if isinstance(target, collections.abc.MutableSet):
            target |= source
        elif isinstance(target, collections.abc.Set):
            return target | source
        else:
            return copy.deepcopy(source)
    elif not isinstance(source, str | collections.abc.ByteString) and \
            isinstance(source, collections.abc.Sequence):
        if isinstance(target, collections.abc.MutableSequence):
            for v in source:
                target.append(v)
        elif not isinstance(target, str | collections.abc.ByteString) and \
                isinstance(target, collections.abc.Sequence):
            return tuple(itertools.chain(target, source))
        else:
            return copy.deepcopy(source)
    elif source is not None or allow_none:
        return source

    return target


def configure_logging(log_level: str, dict_config: dict = None):
    dict_config = dict_config or get_dict_config_defaults()
    logging.config.dictConfig(dict_config.copy())

    root = logging.getLogger()
    root.setLevel(log_level.upper())


def get_dict_config_defaults() -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "asyncio": {"level": "WARNING"},
        },
        "root": {
            "level": "NOTSET",
            "handlers": ["console"],
        }
    }


def load_config_from_yaml(file_path: str) -> dict:
    return yaml.safe_load(Path(file_path).read_text())


@inject
def configure_logging_from_config(config):
    if config.get("log_config"):
        file_config = load_config_from_yaml(config.log_config)
        logging_config = deep_merge(get_dict_config_defaults(), file_config)
    else:
        logging_config = None
    configure_logging(config.log_level, logging_config)
