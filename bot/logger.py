import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger():
    logger = logging.getLogger("Movie-Tracker-Bot")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    file = RotatingFileHandler(
        filename="bot.log",
        maxBytes=20 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file.setLevel(logging.DEBUG)
    file.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console)
        logger.addHandler(file)

    return logger

logger = setup_logger()
