
import os
import logging
from model.mod import Mod
from utils.file_manager import FileManager
from utils.settings_manager import Paths
from utils.lslib import LSLib


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
            return unpacked_mods
        except Exception as e:
            logging.error(f"An error occurred while unpacking mods: {e}")

    @staticmethod
    def select_progression_mods():
        try:
            mods = []
            mod_folders = ModManager.unpack_mods()
            logging.info("Selecting patch compatible mods...")
            # logging.debug(f"{len(mod_folders)} mod folders found")
            for mod_folder in mod_folders:
                meta_file = FileManager.find_files(mod_folder, ['meta.lsx'])
                progression_file = FileManager.find_files(mod_folder, ['Progressions.lsx'])
                class_descriptions_file = FileManager.find_files(mod_folder, ['ClassDescriptions.lsx'])
                if (progression_file):

                    if (class_descriptions_file):
                        mods.append(Mod(meta_file['meta.lsx'], progression_file['Progressions.lsx'], class_descriptions_file['ClassDescriptions.lsx']))
                    else:
                        mods.append(Mod(meta_file['meta.lsx'], progression_file['Progressions.lsx']))
            logging.info(f"{len(mods)} mods selected for patching:")
            for mod in mods:
                logging.info(f"--{mod.name}")
            return mods
        except Exception as e:
            logging.error(f"An error occurred while selecting patch compatible mods: {e}")

    @staticmethod
    def combine_mods():
        try:
            mods = ModManager.select_progression_mods()
            logging.info("Combining mods...")
            patch = Mod()
            for mod in mods:
                for progression in mod.progressions:
                    existing_progression = next((p for p in patch.progressions if p.uuid == progression.uuid), None)
                    if existing_progression:
                        # Merge subclasses if progression already exists
                        existing_subclass_uuids = {s['UUID'] for s in existing_progression.subclasses}
                        new_subclasses = [s for s in progression.subclasses if s['UUID'] not in existing_subclass_uuids]
                        existing_progression.subclasses.extend(new_subclasses)
                        # Merge all attributes
                        for attr in ['boosts', 'passives_added', 'passives_removed' 'selectors', 'allow_improvement', 'is_multiclass']:
                            existing_attr_value = getattr(existing_progression, attr, None)
                            new_attr_value = getattr(progression, attr, None)

                            if existing_attr_value in [None, ""] or new_attr_value in [None, ""]:
                                continue  # Skip merging for this attribute
                            existing_attr_values = set(existing_attr_value.split(';'))
                            new_attr_values = set(new_attr_value.split(';'))
                            merged_attr_values = existing_attr_values.union(new_attr_values)
                            setattr(existing_progression, attr, ';'.join(merged_attr_values))
                    else:
                        # Add progression if it doesn't exist
                        patch.progressions.append(progression)
            logging.info("Mods combined successfully")
            return patch
        except Exception as e:
            logging.error(f"An error occurred while combining mods: {e}")

    @staticmethod
    def create_patch():
        try:
            logging.info("Creating patch...")
            patch = ModManager.combine_mods()
            meta_file_path = os.path.join(Paths.TEMP_DIR, patch.folder, "Mods", patch.folder, "meta.lsx")
            progressions_file_path = os.path.join(Paths.TEMP_DIR, patch.folder, "Public", patch.folder, "Progressions", "Progressions.lsx")
            FileManager.create_file(meta_file_path)
            FileManager.create_file(progressions_file_path)
            FileManager.write_file(meta_file_path, patch.meta_string())
            FileManager.write_file(progressions_file_path, patch.progressions_string())
            logging.info("Patch created successfully")
            ModManager.pack_patch(patch)
            return patch, True
        except Exception as e:
            logging.error(f"An error occurred while creating patch: {e}")

    @staticmethod
    def pack_patch(patch):
        try:
            logging.info("Packing patch...")
            source_path = os.path.join(Paths.TEMP_DIR, patch.folder)
            dest_path = os.path.join(Paths.MOD_LIST_DIR, patch.folder + ".pak")
            LSLib.execute_command("create-package", source_path, dest_path)
            logging.info("Patch packed successfully")
            logging.info("Cleaning up temporary files...")
            ModManager.install_patch(patch)
            # FileManager.clean_folder(Paths.TEMP_DIR)
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
