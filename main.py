import logging
import os
from utils.mod_manager import ModManager
from utils.file_manager import FileManager
from utils.debug import setup_logger
from utils.settings_manager import Paths
from utils.lslib import LSLib


def main():
    setup_logger("DEBUG")
    mod_manager = ModManager()
    patch = mod_manager.create_patch()
    if (patch):
        os.startfile(Paths.MOD_LIST_DIR)


if __name__ == '__main__':
    main()
