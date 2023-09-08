import logging
import os

from utils.debug import setup_logger
from utils.mod_manager import ModManager
from utils.file_manager import FileManager
from utils.settings_manager import Paths
from model.mod import Mod
from model.progression import Progression


def main():
    setup_logger("DEBUG")

    mod_manager = ModManager()
    unpacked_mods = mod_manager.unpack_mods()
    compatible_mods = mod_manager.select_progression_mods(unpacked_mods)
    patch_data = mod_manager.combine_mods(compatible_mods)
    # FileManager.write_file("D:\Projects\Mods\Baldurs Gate 3\BG3ModPatcher\logs\meta.lsx", patch_data.meta_string())
    # FileManager.write_file("D:\Projects\Mods\Baldurs Gate 3\BG3ModPatcher\logs\Progressions.lsx", patch_data.progressions_string())
    # logging.debug(patch_data.folder)

    mod_manager.create_patch_folder(patch_data)
    mod_manager.pack_patch(patch_data, Paths.MOD_LIST_DIR)
    mod_manager.install_patch(patch_data)
    # mod_manager.clean_up()
    # input("Press Enter to continue...")


if __name__ == '__main__':
    main()
