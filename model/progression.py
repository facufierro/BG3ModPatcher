from typing import List, Optional
import logging
from lxml import etree
from model.subclass import SubClass


class Progression:
    def __init__(self, uuid: str, name: str, table_uuid: str, level: int,
                 allow_improvement: bool = None,
                 is_multiclass: bool = None,
                 boosts: Optional[List[str]] = None,
                 passives_added: Optional[List[str]] = None,
                 passives_removed: Optional[List[str]] = None,
                 selectors: Optional[List[str]] = None,
                 subclasses: Optional[List[SubClass]] = None):
        try:
            self.uuid = uuid
            self.name = name
            self.table_uuid = table_uuid
            self.level = level
            self.allow_improvement = allow_improvement
            self.is_multiclass = is_multiclass
            self.boosts = boosts or []
            self.passives_added = passives_added or []
            self.passives_removed = passives_removed or []
            self.selectors = selectors or []
            self.subclasses = subclasses or []
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression: {e}")

    @staticmethod
    def load_progression_from_xml(xml_string: str) -> 'Progression':
        try:
            root = etree.fromstring(xml_string)

            uuid = root.xpath(".//attribute[@id='UUID']/@value")[0]
            name = root.xpath(".//attribute[@id='Name']/@value")[0]
            table_uuid = root.xpath(".//attribute[@id='TableUUID']/@value")[0]
            level = int(root.xpath(".//attribute[@id='Level']/@value")[0])

            allow_improvement_values = root.xpath(".//attribute[@id='AllowImprovement']/@value")
            allow_improvement = bool(allow_improvement_values[0]) if allow_improvement_values else None

            is_multiclass_values = root.xpath(".//attribute[@id='IsMulticlass']/@value")
            is_multiclass = bool(is_multiclass_values[0]) if is_multiclass_values else None

            boosts_values = root.xpath(".//attribute[@id='Boosts']/@value")
            boosts = boosts_values[0].split(';') if boosts_values else []

            passives_added_values = root.xpath(".//attribute[@id='PassivesAdded']/@value")
            passives_added = passives_added_values[0].split(';') if passives_added_values else []

            passives_removed_values = root.xpath(".//attribute[@id='PassivesRemoved']/@value")
            passives_removed = passives_removed_values[0].split(';') if passives_removed_values else []

            selectors_values = root.xpath(".//attribute[@id='Selectors']/@value")
            selectors = selectors_values[0].split(';') if selectors_values else []

            sub_class_elements = root.xpath(".//node[@id='SubClasses']/children/node")
            subclasses = [SubClass(el.xpath(".//attribute[@id='Object']/@value")[0]) for el in sub_class_elements] if sub_class_elements else []

            return Progression(uuid, name, table_uuid, level, allow_improvement, is_multiclass, boosts, passives_added, passives_removed, selectors, subclasses)
        except Exception as e:
            logging.error(f"An error occurred while loading a Progression from XML: {e}")

    def __str__(self) -> str:
        try:
            optional_attributes = []

            if self.boosts:
                optional_attributes.append(self.boosts_string())
            if self.passives_added:
                optional_attributes.append(self.passives_added_string())
            if self.passives_removed:
                optional_attributes.append(self.passives_removed_string())
            if self.selectors:
                optional_attributes.append(self.selectors_string())

            if self.allow_improvement != None:
                optional_attributes.append(self.allow_improvement_string())
            if self.is_multiclass != None:
                optional_attributes.append(self.is_multiclass_string())
            return (
                f'\n\n<!-- {self.name} -->'
                f'\n<node id="Progression">'
                f'\n  <attribute id="UUID" type="guid" value="{self.uuid}"/>'
                f'\n  <attribute id="Name" type="LSString" value="{self.name}"/>'
                f'\n  <attribute id="TableUUID" type="guid" value="{self.table_uuid}"/>'
                f'\n  <attribute id="Level" type="uint8" value="{self.level}"/>'
                f'\n  <attribute id="ProgressionType" type="uint8" value="0"/>'
                f'{"".join(optional_attributes)}'
                f'{self.subclasses_string()}'
                '\n</node>'
            )
        except Exception as e:
            logging.error(f"An error occurred while creating Progression.__str__: {e}")

    def boosts_string(self) -> str:
        try:
            # Ensure all elements in the list are strings
            if all(isinstance(item, str) for item in self.boosts):
                value_string = ';'.join(self.boosts)
                return f'\n<attribute id="Boosts" type="LSString" value="{value_string}"/>'
            else:
                logging.error("boosts should only contain strings.")
                return ""
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression.boosts_string: {e}")
            return ""

    def passives_added_string(self) -> str:
        try:
            if all(isinstance(item, str) for item in self.passives_added):
                value_string = ';'.join(self.passives_added)
                return f'\n<attribute id="PassivesAdded" type="LSString" value="{value_string}"/>'
            else:
                logging.error("passives_added should only contain strings.")
                return ""
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression.passives_added_string: {e}")
            return ""

    def passives_removed_string(self) -> str:
        try:
            if all(isinstance(item, str) for item in self.passives_removed):
                value_string = ';'.join(self.passives_removed)
                return f'\n<attribute id="PassivesRemoved" type="LSString" value="{value_string}"/>'
            else:
                logging.error("passives_removed should only contain strings.")
                return ""
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression.passives_removed_string: {e}")
            return ""

    def selectors_string(self) -> str:
        try:
            if all(isinstance(item, str) for item in self.selectors):
                value_string = ';'.join(self.selectors)
                return f'\n<attribute id="Selectors" type="LSString" value="{value_string}"/>'
            else:
                logging.error("selectors should only contain strings.")
                return ""
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression.selectors_string: {e}")
            return ""

    def allow_improvement_string(self) -> str:
        try:
            return (f'\n<attribute id="AllowImprovement" type="bool" value="{self.allow_improvement}"/>')
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression.allow_improvement_string: {e}")

    def is_multiclass_string(self) -> str:
        try:
            return (f'\n<attribute id="IsMulticlass" type="bool" value="{self.is_multiclass}"/>')
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression.is_multiclass_string: {e}")

    def subclasses_string(self) -> str:
        try:
            subclass_nodes = ''
            for subclass in self.subclasses:
                subclass_nodes += f'{subclass.__str__()}'
            if self.subclasses:
                subclass_nodes = (
                    f'\n<children>'
                    f'\n<node id="SubClasses">'
                    f'\n<children>'
                    f'\n{subclass_nodes}'
                    f'\n</children>'
                    f'\n</node>'
                    f'\n</children>'
                )
            return subclass_nodes
        except Exception as e:
            logging.error(f"An error occurred while creating a Progression.subclasses_string: {e}")
