from model.class_description import ClassDescription
from difflib import SequenceMatcher
import logging


class Icon:
    def __init__(self, class_description: ClassDescription, mod_folder: str) -> None:
        try:
            self.class_description = class_description
            self.mod_folder = mod_folder
            self.icon_type = self.get_icon_type()
            self.icon_name = class_description.name
            self.icon_hotbar_name = class_description.name
        except Exception as e:
            logging.error(f"An error occurred while creating an Icon: {e}")

    def get_icon_type(self) -> str:
        try:
            if self.class_description.parent_guid is None:
                return "Class"
            else:
                return "Subclass"
        except Exception as e:
            logging.error(f"An error occurred while getting an Icon's type: {e}")

    def set_icon_name(self, icon_names_list: list) -> None:
        closest_match = ""
        highest_ratio = 0

        for icon_name in icon_names_list:
            ratio = SequenceMatcher(None, icon_name, self.icon_name).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                closest_match = icon_name

        self.icon_name = closest_match

    def icon_string(self) -> str:
        return (
            f'<DataTrigger Binding="{{Binding IDString}}" Value="{self.class_description.name}">'
            f'<Setter Property="Source" Value="pack://application:,,,/GustavNoesisGUI;component/Assets/{self.mod_folder}/ClassIcons/{self.icon_name}.png"/>'
            '</DataTrigger>')

    def icon_hotbar_string(self) -> str:
        return (
            f'<DataTrigger Binding="{{Binding IDString}}" Value="{self.class_description.name}">'
            f'<Setter Property="Source" Value="pack://application:,,,/GustavNoesisGUI;component/Assets/{self.mod_folder}/ClassIcons/hotbar/{self.icon_name}.png"/>'
            '</DataTrigger>')
