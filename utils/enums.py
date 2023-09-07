from enum import Enum
from utils.settings_manager import Paths


class FileType(Enum):
    ENGLISH_LOCALIZATION = Paths.ENGLISH_LOCALIZATION_DIR
    ICONS = Paths.ICONS_DIR
    OBJECT = Paths.OBJECT_DIR
    PROGRESSION = Paths.PROGRESSION_DIR
    ROOT_TEMPLATES = Paths.ROOT_TEMPLATES_DIR
    SHOUT = Paths.SHOUT_DIR
