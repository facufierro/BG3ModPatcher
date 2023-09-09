
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
    def select_progression_mods(unpacked_mods: List[str]):
        try:
            mods = []
            logging.warn("Only mods with COMPATIBLE meta.lsx and Progressions.lsx file will be selected. Other mods are not supported by this tool.")
            # logging.info("Selecting patch compatible mods...")

            for unpacked_mod in unpacked_mods:

                unpacked_mod_folder = os.path.basename(os.path.normpath(unpacked_mod))
                if unpacked_mod_folder == "ImprovedUI Assets":
                    logging.warn(f"ImprovedUI Assets mod detected. Icons will be patched.")
                    continue
                logging.info(f"Analyzing {unpacked_mod_folder} mod...")
                meta_file = FileManager.find_files(unpacked_mod, ['meta.lsx'])
                progression_file = FileManager.find_files(unpacked_mod, ['Progressions.lsx'])

                if meta_file:
                    meta_string = FileManager.xml_to_string(meta_file['meta.lsx'])
                    meta_string = meta_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')

                    if progression_file:
                        progression_string = FileManager.xml_to_string(progression_file['Progressions.lsx'])
                        if progression_string is None:
                            logging.warning(f"Progressions.lsx file in mod: {unpacked_mod_folder} is not valid. Skipping mod...")
                            continue
                        progression_string = progression_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                        mod = Mod(meta_string, progression_string)
                        if mod.progressions is None:
                            continue
                        mods.append(mod)
                        # logging.info(f"-- {unpacked_mod_folder} selected for patching.")

            logging.info(f"{len(mods)} mods selected for patching:")
            for mod in mods:
                logging.info(f"--{mod.name}")

            return mods

        except Exception as e:
            # logging.error(f"An error occurred while selecting patch compatible mods: {e}")
            pass

    @staticmethod
    def combine_mods(mods: List[Mod]):
        patch_data = Mod()
        for mod in mods:
            logging.debug(f"Combining mod: {mod.name}")
            if mod.progressions is None:
                logging.warning(f"No progressions in mod: {mod.name}")
                continue

            for new_progression in mod.progressions:
                existing_progression = next((p for p in patch_data.progressions if p.uuid == new_progression.uuid), None)
                if existing_progression:
                    ModManager.merge_progressions(existing_progression, new_progression)
                else:
                    patch_data.progressions.append(new_progression)

            for patch_progression in patch_data.progressions:
                ModManager.remove_value_duplicates(patch_progression)
                ModManager.remove_duplicate_spellslots(patch_progression)

        logging.info(f"Successfully combined {len(mods)} mods into {patch_data.name}")
        # logging.debug(f"Attributes of patch_data: {vars(patch_data)}")

        return patch_data

    @staticmethod
    def combine_icons(mods: List[Mod]):
        try:
            logging.info("Combining icons...")
            class_icons_file = FileManager.find_files(Paths.TEMP_DIR, ["IUI_ClassIcons.xaml"])
            race_icons_file = FileManager.find_files(Paths.TEMP_DIR, ["IUI_RaceIcons.xaml"])

           
            # for mod in mods:
            #     if mod.icons is None:
            #         continue
            #     for icon in mod.icons:
            #         icon_files.append(icon)
            logging.info(f"Successfully combined icons for {len(mods)} mods ")
        except Exception as e:
            logging.error(f"An error occurred while combining icons: {e}")

    @staticmethod
    def create_patch_folder(patch_data: Mod):
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
    def pack_patch(patch_data: Mod):
        try:
            logging.info("Packing patch...")
            source_path = os.path.join(Paths.TEMP_DIR, patch_data.folder)
            dest_path = os.path.join(Paths.MOD_LIST_DIR, patch_data.folder + ".pak")
            LSLib.execute_command("create-package", source_path, dest_path)
            logging.info("Patch packed successfully")
        except Exception as e:
            logging.error(f"An error occurred while packing patch: {e}")

    @staticmethod
    def install_patch(patch_data: Mod):
        try:
            logging.info("Installing patch...")
            modsettings_file = FileManager.find_files(Paths.GAME_DATA_DIR, ["modsettings.lsx"])
            FileManager.insert_after_last_node(modsettings_file['modsettings.lsx'], "Module", patch_data.module_string())
            FileManager.insert_after_last_node(modsettings_file['modsettings.lsx'], "ModuleShortDesc", patch_data.module_short_desc_string())
            logging.info("Patch installed successfully")
            return True
        except Exception as e:
            logging.error(f"An error occurred while installing patch: {e}")

    @staticmethod
    def merge_progressions(existing_progression: Progression, new_progression: Progression):
        try:
            existing_subclass_uuids = [s.uuid for s in existing_progression.subclasses]
            new_subclasses = [s for s in new_progression.subclasses if s.uuid not in existing_subclass_uuids]
            existing_progression.subclasses.extend(new_subclasses)

            for attr in ['boosts', 'passives_added', 'passives_removed', 'selectors', 'allow_improvement', 'is_multiclass']:
                existing_attr = getattr(existing_progression, attr, None)
                new_attr = getattr(new_progression, attr, None)
                setattr(existing_progression, attr, ModManager.merge_attributes(existing_attr, new_attr))
        except Exception as e:
            logging.error(f"An error occurred while merging progressions: {e}")

    @staticmethod
    def merge_attributes(existing_progression: Progression, new_progression: Progression):
        try:
            if existing_progression is None or new_progression is None:
                return existing_progression or new_progression

            if isinstance(existing_progression, str) and isinstance(new_progression, str):
                return ';'.join(set(existing_progression.split(';')).union(set(new_progression.split(';'))))
            elif isinstance(existing_progression, list) and isinstance(new_progression, list):
                return list(set(existing_progression).union(set(new_progression)))
            else:
                return existing_progression
        except Exception as e:
            logging.error(f"An error occurred while merging attributes: {e}")

    @staticmethod
    def remove_value_duplicates(progression: Progression):
        try:
            attributes = ["boosts", "passives_added", "passives_removed", "selectors"]
            for attribute in attributes:
                attr_value = getattr(progression, attribute, None)
                if attr_value is not None:
                    unique_values = list(set(attr_value))
                    setattr(progression, attribute, unique_values)
        except Exception as e:
            logging.error(f"An error occurred while removing value duplicates: {e}")

    @staticmethod
    def remove_duplicate_spellslots(progression: Progression):
        try:
            if progression.boosts is None:
                return

            highest_level_for_slot = {}

            for boost in progression.boosts:
                if "ActionResource(SpellSlot," in boost:
                    parts = boost.split(",")
                    level = int(parts[1])
                    slots = int(parts[2].replace(")", ""))

                    if level > highest_level_for_slot.get(slots, 0):
                        highest_level_for_slot[slots] = level

            new_boosts = [boost for boost in progression.boosts if "ActionResource(SpellSlot," not in boost]

            for slots, level in highest_level_for_slot.items():
                new_boosts.append(f"ActionResource(SpellSlot,{level},{slots})")

            progression.boosts = new_boosts
        except Exception as e:
            logging.error(f"An error occurred while removing duplicate spellslots: {e}")

    @staticmethod
    def clean_up():
        try:
            logging.info("Cleaning temporary files...")
            FileManager.clean_folder(Paths.TEMP_DIR)
            logging.info("Temporary files cleaned successfully")
        except Exception as e:
            logging.error(f"An error occurred while cleaning up: {e}")
