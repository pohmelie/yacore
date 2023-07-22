import logging
import sys

from click import Choice
from cock import Option, build_options_from_dict
from loguru import logger

from yacore.injector import inject

log_options = build_options_from_dict({
    "log-level": Option(default="debug", type=Choice(["debug", "info", "warning", "error"])),
})


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logging(log_level):
    logger.configure(
        handlers=[
            dict(
                sink=sys.stderr,
                # format="{time} {level:<8} {message}",
                level=log_level.upper(),
            ),
        ],
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


@inject
def configure_logging_from_config(config):
    configure_logging(config.log_level)
