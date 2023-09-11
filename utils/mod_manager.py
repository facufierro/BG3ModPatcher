
import os
import logging
from typing import List
from lxml import etree
from model.mod import Mod
from utils.file_manager import FileManager
from utils.settings_manager import Paths
from utils.lslib import LSLib
from model.progression import Progression


class ModManager:
    ImprovedUI_Assets = False

    @staticmethod
    def get_mod_list():
        lstMods = []
        mods_directory = Paths.MOD_LIST_DIR

        try:
            for filename in os.listdir(mods_directory):
                if filename.endswith(".pak"):
                    if filename == "FFTCompatibilityPatch.pak":
                        continue
                    lstMods.append(filename)
        except Exception as e:
            logging.error(f"An error occurred while listing all mods: {e}")

        return lstMods

    @staticmethod
    def unpack_mods() -> List[str]:
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
    def get_mods_list(unpacked_mods: List[str]) -> List[Mod]:
        mods = []
        for unpacked_mod in unpacked_mods:
            unpacked_mod_folder = os.path.basename(os.path.normpath(unpacked_mod))
            if unpacked_mod_folder == "FFTCompatibilityPatch":
                continue
            if unpacked_mod_folder == "ImprovedUI Assets":
                ModManager.ImprovedUI_Assets = True
            meta_file = FileManager.find_files(unpacked_mod, ['meta.lsx'])
            class_descriptions_file = FileManager.find_files(unpacked_mod, ['ClassDescriptions.lsx'])
            progression_file = FileManager.find_files(unpacked_mod, ['Progressions.lsx'])

            if meta_file:
                meta_string = FileManager.xml_to_string(meta_file['meta.lsx'])
                meta_string = meta_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                if class_descriptions_file:
                    class_descriptions_string = FileManager.xml_to_string(class_descriptions_file['ClassDescriptions.lsx'])
                    class_descriptions_string = class_descriptions_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')

                    if progression_file:
                        progression_string = FileManager.xml_to_string(progression_file['Progressions.lsx'])
                        progression_string = progression_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')

                        # Create the Mod object here, within the innermost if block
                        mod = Mod(unpacked_mod, meta_string, class_descriptions_string, progression_string)
                        ModManager.load_icons(mod, unpacked_mod)
                        mods.append(mod)
        return mods

    @staticmethod
    def load_icons(mod, unpacked_mod):
        try:
            icon_folder = FileManager.find_folders(unpacked_mod, ['ClassIcons'])
            icon_names = FileManager.get_file_names(icon_folder['ClassIcons'], 'DDS')
            for icon in mod.icons:
                icon.set_icon_name(icon_names)
                # logging.debug(f"Icon: {icon.icon_name} - {icon.icon_type}")
            logging.info(f"Loaded {len(mod.icons)} icons for {mod.name}")
        except Exception as e:
            logging.error(f"An error occurred while loading icons: {e}")

    @staticmethod
    def select_progression_mods(mod_list: List[Mod]) -> List[Mod]:
        try:
            logging.info("Selecting mods for patching...")
            logging.warn("Only mods with COMPATIBLE meta.lsx and Progressions.lsx file will be selected. Other mods don't need Progression patching.")

            compatible_mods = mod_list
            for mod in compatible_mods:
                if mod.progressions is None:
                    compatible_mods.remove(mod)

            logging.info(f"Selected {len(compatible_mods)} mods for progression patching")
            for compatible_mod in compatible_mods:
                logging.debug(f"--{compatible_mod.name}")
            return compatible_mods
        except Exception as e:
            logging.error(f"An error occurred while selecting patch compatible mods: {e}")

    @staticmethod
    def combine_mods(mods: List[Mod]) -> Mod:
        patch_data = Mod()
        for mod in mods:
            logging.debug(f"Combining progressions for {mod.name}...")

            for new_progression in mod.progressions:
                existing_progression = next((p for p in patch_data.progressions if p.uuid == new_progression.uuid), None)
                if existing_progression:
                    ModManager.merge_progressions(existing_progression, new_progression)
                else:
                    patch_data.progressions.append(new_progression)

            for patch_progression in patch_data.progressions:
                ModManager.remove_value_duplicates(patch_progression)
                ModManager.remove_duplicate_spellslots(patch_progression)

        logging.info(f"Successfully combined progressions for {len(mods)} mods into {patch_data.name}")
        return patch_data

    @staticmethod
    def combine_icons(mods: List[Mod]) -> None:
        try:
            if ModManager.ImprovedUI_Assets:
                logging.warn(f"ImprovedUI Assets detected. Icons will be patched.")
                logging.info("Combining icons...")
                patch_class_icons_file = os.path.join(Paths.TEMP_DIR, "FFTCompatibilityPatch", "Public", "Game", "GUI", "Library", "IUI_ClassIcons.xaml")
                mod: Mod
                for mod in mods:
                    for mod_icon in mod.icons:
                        logging.debug(mod_icon.icon_string())
                        # FileManager.insert_string_to_xml(patch_class_icons_file, "//DataTrigger[@Binding='{Binding SubclassIDString}']", mod_icon.icon_string(), namespace='default')
                        FileManager.insert_string_to_xml(
                            patch_class_icons_file,
                            f"//DataTrigger[@Binding='{{Binding {mod_icon.icon_type}IDString}}']",
                            mod_icon.icon_string(),
                            namespace='default',
                            position='first')
                        FileManager.insert_string_to_xml(
                            patch_class_icons_file,
                            f"//DataTrigger[@Binding='{{Binding {mod_icon.icon_type}IDString}}']",
                            mod_icon.icon_hotbar_string(),
                            namespace='default',
                            position='last')
                logging.info("Successfully combined icons")
        except Exception as e:
            logging.error(f"An error occurred while combining icons: {e}")

    @staticmethod
    def create_patch_folder(patch_data: Mod, unpacked_mod_folders: List[str]) -> bool:
        try:
            logging.info("Creating patch files...")

            meta_file_path = os.path.join(Paths.TEMP_DIR, patch_data.folder, "Mods", patch_data.folder, "meta.lsx")
            progressions_file_path = os.path.join(Paths.TEMP_DIR, patch_data.folder, "Public", patch_data.folder, "Progressions", "Progressions.lsx")
            FileManager.create_file(meta_file_path)
            FileManager.create_file(progressions_file_path)
            FileManager.write_file(meta_file_path, patch_data.meta_string())
            FileManager.write_file(progressions_file_path, patch_data.progressions_string())

            if ModManager.ImprovedUI_Assets:

                improvedui_library_folder = os.path.join(Paths.TEMP_DIR, "ImprovedUI Assets", "Public", "Game", "GUI", "Library")
                patch_library_folder = os.path.join(Paths.TEMP_DIR, "FFTCompatibilityPatch", "Public", "Game", "GUI", "Library")
                FileManager.copy_folder(improvedui_library_folder, patch_library_folder)
                patch_assets_folder = os.path.join(Paths.TEMP_DIR, "FFTCompatibilityPatch", "Public", "Game", "GUI", "Assets")
                for unpacked_mod_folder in unpacked_mod_folders:
                    assets_folder = os.path.join(Paths.TEMP_DIR, unpacked_mod_folder, "Public", "Game", "GUI", "Assets")
                    FileManager.copy_folder(assets_folder, patch_assets_folder)
            logging.info("Patch files created successfully")
            return True
        except Exception as e:
            logging.error(f"An error occurred while creating the patch files: {e}")

    @staticmethod
    def pack_patch(patch_data: Mod) -> bool:
        try:
            logging.info("Packing patch...")
            source_path = os.path.join(Paths.TEMP_DIR, patch_data.folder)
            dest_path = os.path.join(Paths.MOD_LIST_DIR, patch_data.folder + ".pak")
            LSLib.execute_command("create-package", source_path, dest_path)
            logging.info("Patch packed successfully")
        except Exception as e:
            logging.error(f"An error occurred while packing patch: {e}")

    @staticmethod
    def install_patch(patch_data: Mod) -> bool:
        try:
            logging.info("Installing patch...")
            modsettings_file = FileManager.find_files(Paths.GAME_DATA_DIR, ["modsettings.lsx"])
            FileManager.insert_string_to_xml(modsettings_file['modsettings.lsx'], "//node[@id='Module']", patch_data.module_string())
            FileManager.insert_string_to_xml(modsettings_file['modsettings.lsx'], "//node[@id='ModuleShortDesc']", patch_data.module_short_desc_string())
            logging.info("Patch installed successfully")
            return True
        except Exception as e:
            logging.error(f"An error occurred while installing patch: {e}")

    @staticmethod
    def merge_progressions(existing_progression: Progression, new_progression: Progression) -> None:
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
    def merge_attributes(existing_progression: Progression, new_progression: Progression) -> None:
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
    def remove_value_duplicates(progression: Progression) -> None:
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
    def remove_duplicate_spellslots(progression: Progression) -> None:
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
    def clean_up() -> None:
        try:
            logging.info("Cleaning temporary files...")
            FileManager.clean_folder(Paths.TEMP_DIR)
            logging.info("Temporary files cleaned successfully")
        except Exception as e:
            logging.error(f"An error occurred while cleaning up: {e}")
