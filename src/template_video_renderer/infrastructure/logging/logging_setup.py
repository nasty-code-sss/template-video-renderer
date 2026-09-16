import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
LOGGER_NAME = "template_video_renderer"


def configure_logging(level: str) -> logging.Logger:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger
