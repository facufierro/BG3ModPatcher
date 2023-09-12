import logging

from utils.debug import setup_logger
from utils.mod_manager import ModManager


def main():
    info_level = "DEBUG"
    setup_logger(info_level)
    logging.info("Starting BG3ModPatcher v2.0.1 by fierrof")
    mod_manager = ModManager()
    unpacked_mods = mod_manager.unpack_mods()
    mods_list = mod_manager.get_mods_list(unpacked_mods)
    compatible_mods = mod_manager.select_progression_mods(mods_list)
    patch_data = mod_manager.combine_mods(compatible_mods)

    mod_manager.create_patch_folder(patch_data, unpacked_mods)
    # mod_manager.combine_icons(mods_list)
    mod_manager.pack_patch(patch_data)
    mod_manager.install_patch(patch_data)
    if info_level == "INFO":
        mod_manager.clean_up()
        input("Press Enter to continue...")


if __name__ == '__main__':
    main()
