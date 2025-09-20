import logging
from typing import ClassVar


class CustomFormatter(logging.Formatter):
    colors: ClassVar = {
        logging.DEBUG: "\033[34m",  # Blue
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[31m",  # Red
        logging.ERROR: "\033[38;5;52m",  # Dark red
    }
    reset = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.colors.get(record.levelno)
        name = f"{color}{record.levelname}{self.reset}"
        message = f"{color}{record.msg}{self.reset}"
        record.levelname = name
        record.msg = message
        return super().format(record)


def setup_logger(level: int | str, logger: logging.Logger) -> None:
    handler = logging.StreamHandler()
    formatter = CustomFormatter("%(levelname)s: %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
