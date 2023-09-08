
import os
import logging
from typing import List
from model.mod import Mod
from utils.file_manager import FileManager
from utils.settings_manager import Paths
from utils.lslib import LSLib
from model.progression import Progression


class ModManager:
    @staticmethod
    def get_mod_list():
        lstMods = []
        mods_directory = Paths.MOD_LIST_DIR

        try:
            for filename in os.listdir(mods_directory):
                if filename.endswith(".pak"):
                    lstMods.append(filename)
        except Exception as e:
            logging.error(f"An error occurred while listing all mods: {e}")

        return lstMods

    @staticmethod
    def unpack_mods():
        try:
            logging.info("Unpacking mods...")
            unpacked_mods = []
            FileManager.create_folder(Paths.TEMP_DIR)
            FileManager.clean_folder(Paths.TEMP_DIR)
            for mod in ModManager.get_mod_list():
                source_path = os.path.join(Paths.MOD_LIST_DIR, mod)
                dest_path = os.path.join(Paths.TEMP_DIR, mod[:-4])

                LSLib.execute_command("extract-package", source_path, dest_path)
                unpacked_mods.append(dest_path)
            logging.info("Mods unpacked successfully")
            for mod in unpacked_mods:
                logging.debug(f"Unpacked mod: {mod}")
            return unpacked_mods
        except Exception as e:
            logging.error(f"An error occurred while unpacking mods: {e}")

    @staticmethod
    def select_progression_mods(unpacked_mods):
        try:
            mods = []
            logging.info("Selecting patch compatible mods...")
            logging.warn("Only mods with a meta.lsx and Progressions.lsx file will be selected. Other mods are not supported by this tool.")
            for unpacked_mod in unpacked_mods:
                meta_file = FileManager.find_files(unpacked_mod, ['meta.lsx'])
                progression_file = FileManager.find_files(unpacked_mod, ['Progressions.lsx'])

                if meta_file:

                    meta_string = FileManager.xml_to_string(meta_file['meta.lsx'])
                    meta_string = meta_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')

                    if progression_file:
                        progression_string = FileManager.xml_to_string(progression_file['Progressions.lsx'])
                        # logging.debug(f"Progression string: {progression_string}")
                        progression_string = progression_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                        mods.append(Mod(meta_string, progression_string))

            logging.info(f"{len(mods)} mods selected for patching:")
            for mod in mods:
                logging.info(f"--{mod.name}")

            return mods

        except Exception as e:
            logging.error(f"An error occurred while selecting patch compatible mods: {e}")

    @staticmethod
    def combine_mods(mods: List[Mod]):
        try:
            logging.info("Combining mods...")
            patch_data = Mod()
            mod: Mod
            for mod in mods:
                for progression in mod.progressions:
                    if progression not in patch_data.progressions:
                        patch_data.progressions.append(progression)

            FileManager.write_file("D:\Projects\Mods\Baldurs Gate 3\BG3ModPatcher\Progressions.lsx", patch_data.progressions_string(), 'w')
            return patch_data
        except Exception as e:
            logging.error(f"An error occurred while combining mods: {e}")

    @staticmethod
    def create_patch_folder(patch_data):
        try:
            logging.info("Creating patch files...")

            meta_file_path = os.path.join(Paths.TEMP_DIR, patch_data.folder, "Mods", patch_data.folder, "meta.lsx")
            progressions_file_path = os.path.join(Paths.TEMP_DIR, patch_data.folder, "Public", patch_data.folder, "Progressions", "Progressions.lsx")
            FileManager.create_file(meta_file_path)
            FileManager.create_file(progressions_file_path)
            FileManager.write_file(meta_file_path, patch_data.meta_string())
            FileManager.write_file(progressions_file_path, patch_data.progressions_string())
            logging.info("Patch files created successfully")
            return True
        except Exception as e:
            logging.error(f"An error occurred while creating patch: {e}")

    @staticmethod
    def pack_patch(patch):
        try:
            logging.info("Packing patch...")
            source_path = os.path.join(Paths.TEMP_DIR, patch.folder)
            dest_path = os.path.join(Paths.OUTPUT_DIR, patch.folder + ".pak")
            LSLib.execute_command("create-package", source_path, dest_path)
            logging.info("Patch packed successfully")
            logging.info("Cleaning up temporary files...")
            ModManager.install_patch(patch)
            FileManager.clean_folder(Paths.TEMP_DIR)
            logging.info("Temporary files cleaned up successfully")
            return dest_path
        except Exception as e:
            logging.error(f"An error occurred while packing patch: {e}")

    @staticmethod
    def install_patch(patch):
        try:
            logging.info("Installing patch...")
            modsettings_file = FileManager.find_files(Paths.GAME_DATA_DIR, ["modsettings.lsx"])
            FileManager.insert_after_last_node(modsettings_file['modsettings.lsx'], "Module", patch.module_string())
            FileManager.insert_after_last_node(modsettings_file['modsettings.lsx'], "ModuleShortDesc", patch.module_short_desc_string())

            logging.info("Patch installed successfully")
            return True
        except Exception as e:
            logging.error(f"An error occurred while installing patch: {e}")
