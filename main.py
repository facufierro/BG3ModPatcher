import logging
import os

from utils.debug import setup_logger
from utils.mod_manager import ModManager
from utils.settings_manager import Paths
from model.mod import Mod
from model.progression import Progression


def main():
    setup_logger("DEBUG")

    mod_manager = ModManager()
    unpacked_mods = mod_manager.unpack_mods()
    mods = mod_manager.select_progression_mods(unpacked_mods)
    patch_data = mod_manager.combine_mods(mods)
    # patch = mod_manager.create_patch_folder(patch_data)
    # mod_manager.pack_patch(patch)

    # input("Press Enter to continue...")
if __name__ == '__main__':
    main()
