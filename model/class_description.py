from lxml import etree
from uuid import UUID
from typing import Optional
import logging


class ClassDescription:
    def __init__(self, name: str, uuid: str, parent_guid: str = None):
        try:
            self.name = name
            self.uuid = uuid
            self.parent_guid = parent_guid or None
        except Exception as e:
            logging.error(f"An error occurred while creating a ClassDescription: {e}")

    @staticmethod
    def load_from_xml(xml_string: str) -> 'ClassDescription':
        try:
            root = etree.fromstring(xml_string)

            name = root.xpath(".//attribute[@id='Name']/@value")[0]
            uuid = root.xpath(".//attribute[@id='UUID']/@value")[0]

            parent_guid_values = root.xpath(".//attribute[@id='ParentGuid']/@value")
            parent_guid = parent_guid_values[0] if parent_guid_values else None

            return ClassDescription(name, uuid, parent_guid)
        except Exception as e:
            logging.error(f"An error occurred while loading ClassDescription from XML: {e}")
            return None
