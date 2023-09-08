import logging
import os

from utils.debug import setup_logger
from utils.mod_manager import ModManager
from utils.file_manager import FileManager
from utils.settings_manager import Paths
from model.mod import Mod
from model.progression import Progression


def main():
    setup_logger("INFO")
    logging.info("Starting BG3ModPatcher v1.1.0 by fierrof")
    mod_manager = ModManager()
    unpacked_mods = mod_manager.unpack_mods()
    compatible_mods = mod_manager.select_progression_mods(unpacked_mods)
    patch_data = mod_manager.combine_mods(compatible_mods)
    mod_manager.create_patch_folder(patch_data)
    mod_manager.pack_patch(patch_data)
    mod_manager.install_patch(patch_data)
    mod_manager.clean_up()
    logging.info("BG3ModPatcher v1.1.0 finished successfully!")
    input("Press Enter to continue...")

if __name__ == '__main__':
    main()
