# services/debug.py
import logging
import os
from typing import Literal


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'WARNING': '33',  # Yellow
        'INFO': '37',     # White
        'DEBUG': '36',    # Cyan
        'CRITICAL': '41',  # Red
        'ERROR': '31'     # Red
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            return f"\033[1;{self.COLORS[record.levelname]}m{super().format(record)}\033[1;m"
        return super().format(record)


def setup_logger(log_level=Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger = logging.getLogger()
    logger.setLevel(log_level)
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler for debug logs
    debug_file_handler = logging.FileHandler("logs/debug.log")
    debug_file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    debug_file_handler.setFormatter(debug_file_formatter)
    debug_file_handler.setLevel(logging.DEBUG)  # Only debug messages or higher
    logger.addHandler(debug_file_handler)

    # File handler for general logs
    general_file_handler = logging.FileHandler("logs/application.log")
    general_file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    general_file_handler.setFormatter(general_file_formatter)
    general_file_handler.setLevel(logging.INFO)  # Info messages or higher
    logger.addHandler(general_file_handler)

    # Console handler (with colors)
    console_handler = logging.StreamHandler()
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
