# in paths.py
import os


class Paths:

    GAME_DATA_DIR = os.path.join(os.getenv("LOCALAPPDATA"), "Larian Studios", "Baldur's Gate 3")
    MOD_LIST_DIR = os.path.join(GAME_DATA_DIR, "Mods")

    ROOT_DIR = os.getcwd()
    DIVINE_FILE = os.path.join(ROOT_DIR, "export_tool", "divine.exe")
    SETTINGS_FILE = os.path.join(ROOT_DIR, "settings.json")
    OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
    TEMP_DIR = os.path.join(ROOT_DIR, "temp")

    # Enum paths
    ENGLISH_LOCALIZATION_DIR = os.path.join(ROOT_DIR, "EnglishLocalization")
    ICONS_DIR = os.path.join(ROOT_DIR, "Icons")
    OBJECT_DIR = os.path.join(ROOT_DIR, "Object")
    PROGRESSION_DIR = os.path.join(ROOT_DIR, "Progressions")
    ROOT_TEMPLATES_DIR = os.path.join(ROOT_DIR, "RootTemplates")
    SHOUT_DIR = os.path.join(ROOT_DIR, "Spell_Shout")
