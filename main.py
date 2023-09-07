import logging
import os

from utils.debug import setup_logger
from utils.mod_manager import ModManager
from utils.settings_manager import Paths


def main():
    setup_logger("DEBUG")
    logging.info(Paths.DIVINE_FILE)
    mod_manager = ModManager()
    patch = mod_manager.create_patch()
    input("Press Enter to continue...")


if __name__ == '__main__':
    main()
