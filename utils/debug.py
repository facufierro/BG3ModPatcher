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
        log_color = self.COLORS.get(record.levelname, '37')  # Default to white

        if record.levelname == 'INFO' and 'successfully' in record.msg:
            log_color = '32'  # Green for 'SUCCESS' within 'INFO'

        return f"\033[1;{log_color}m{super().format(record)}\033[1;m"


def setup_logger(log_level=Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

        # Clear the logs on start
    with open("logs/debug.log", "w"):
        pass  # Clearing the debug log
    with open("logs/application.log", "w"):
        pass  # Clearing the application log

    logger = logging.getLogger()
    logger.setLevel(log_level)

    if logger.hasHandlers():
        logger.handlers.clear()

    # Add SUCCESS level
    SUCCESS_LEVEL_NUM = 25
    logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

    def success(msg, *args, **kwargs):
        logger.log(SUCCESS_LEVEL_NUM, msg, *args, **kwargs)

    logger.success = success  # Add success method to logger

    # File handlers (keeping your original code for these)
    debug_file_handler = logging.FileHandler("logs/debug.log")
    debug_file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    debug_file_handler.setFormatter(debug_file_formatter)
    debug_file_handler.setLevel(logging.DEBUG)
    logger.addHandler(debug_file_handler)

    general_file_handler = logging.FileHandler("logs/application.log")
    general_file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    general_file_handler.setFormatter(general_file_formatter)
    general_file_handler.setLevel(logging.INFO)
    logger.addHandler(general_file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    colored_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
