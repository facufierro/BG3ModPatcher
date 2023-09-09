import logging
from lxml import etree
from typing import List, Optional
from model.progression import Progression


class Mod:
    def __init__(self, meta_xml_string: str = None, progressions_xml_string: str = None):
        try:
            self.progressions: Optional[List[Progression]] = None

            # Parsing Meta XML
            try:
                if meta_xml_string is not None:
                    meta_root = etree.fromstring(meta_xml_string)

                    module_info = meta_root.xpath(".//node[@id='ModuleInfo']")[0]
                    self.author = module_info.xpath(".//attribute[@id='Author']/@value")[0]
                    self.description = module_info.xpath(".//attribute[@id='Description']/@value")[0]
                    self.folder = module_info.xpath(".//attribute[@id='Folder']/@value")[0]
                    self.name = module_info.xpath(".//attribute[@id='Name']/@value")[0]
                    self.uuid = module_info.xpath(".//attribute[@id='UUID']/@value")[0]
                else:
                    # Default values for meta
                    self.author = "fierrof"
                    self.description = "A compatibility patch for Baldur's Gate 3 mods."
                    self.folder = "FFTCompatibilityPatch"
                    self.name = "FFTCompatibilityPatch"
                    self.uuid = "db6fa677-150a-4302-8aab-ce4b349372bf"
                    self.progressions = []
            except Exception as e:
                logging.error(f"An error occurred while parsing meta.lsx: {e}")
            # Parsing Progressions XML
            try:
                if progressions_xml_string is not None:
                    self.progressions = []
                    prog_root = etree.fromstring(progressions_xml_string)
                    progression_nodes = prog_root.xpath(".//node[@id='Progression']")
                    for node in progression_nodes:
                        xml_string_progression = etree.tostring(node).decode()
                        progression = Progression.load_progression_from_xml(xml_string_progression)
                        if progression is None:
                            # logging.warning(f"Progressions from {self.name} could not be loaded. Skipping mod...")
                            self.progressions = None
                            break
                        else:
                            self.progressions.append(progression)

            except Exception as e:
                logging.error(f"An error occurred while parsing Progressions.lsx: {e}")

        except Exception as e:
            logging.error(f"An error occurred while creating a Mod: {e}")

    def __str__(self):
        str_rep = (
            f"Mod Info:\n"
            f"Author: {self.author}\n"
            f"Description: {self.description}\n"
            f"Folder: {self.folder}\n"
            f"Name: {self.name}\n"
            f"UUID: {self.uuid}\n"
            f"Number of Progressions: {len(self.progressions)}"
        )
        return str_rep

    def meta_string(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<save>'
            '<version major="4" minor="0" revision="8" build="612"/>'
            '<region id="Config">'
            '<node id="root">'
            '<children>'
            '<node id="Dependencies"/>'
            '<node id="ModuleInfo">'
            f'<attribute id="Author" type="LSString" value="{self.author}"/>'
            '<attribute id="CharacterCreationLevelName" type="FixedString" value=""/>'
            f'<attribute id="Description" type="LSString" value="{self.description}"/>'
            f'<attribute id="Folder" type="LSString" value="{self.folder}"/>'
            '<attribute id="LobbyLevelName" type="FixedString" value=""/>'
            '<attribute id="MD5" type="LSString" value=""/>'
            '<attribute id="MainMenuBackgroundVideo" type="FixedString" value=""/>'
            '<attribute id="MenuLevelName" type="FixedString" value=""/>'
            f'<attribute id="Name" type="LSString" value="{self.name}"/>'
            '<attribute id="NumPlayers" type="uint8" value="4"/>'
            '<attribute id="PhotoBooth" type="FixedString" value=""/>'
            '<attribute id="StartupLevelName" type="FixedString" value=""/>'
            '<attribute id="Tags" type="LSString" value=""/>'
            '<attribute id="Type" type="FixedString" value="Add-on"/>'
            f'<attribute id="UUID" type="FixedString" value="{self.uuid}"/>'
            '<attribute id="Version64" type="int64" value="36028797018963968"/>'
            '<children>'
            '<node id="PublishVersion">'
            '<attribute id="Version64" type="int64" value="36028797018963968"/>'
            '</node>'
            '<node id="TargetModes">'
            '<children>'
            '<node id="Target">'
            '<attribute id="Object" type="FixedString" value="Story"/>'
            '</node>'
            '</children>'
            '</node>'
            '</children>'
            '</node>'
            '</children>'
            '</node>'
            '</region>'
            '</save>'
        )

    def progressions_string(self) -> str:
        return (
            '\n<?xml version="1.0" encoding="UTF-8"?>'
            '\n<save>'
            '\n<version major="4" minor="0" revision="9" build="330"/>'
            '\n<region id="Progressions">'
            '\n<node id="root">'
            '\n<children>'
            f'{"".join([str(prog) for prog in self.progressions])}'
            '\n</children>'
            '\n</node>'
            '\n</region>'
            '\n</save>'

        )

    def module_string(self) -> str:
        str = ('<node id="Module">\n'
               f'<attribute id="UUID" value="{self.uuid}" type="FixedString" />\n'
               ' </node>')
        return str

    def module_short_desc_string(self) -> str:
        str = (
            '<node id="ModuleShortDesc">\n'
            f'<attribute id="Folder" value="{self.folder}" type="LSString" />\n'
            '<attribute id="MD5" value="" type="LSString" />\n'
            f'<attribute id="Name" value="{self.name}" type="LSString" />\n'
            f'<attribute id="UUID" value="{self.uuid}" type="FixedString" />\n'
            f'<attribute id="Version64" value="36028797018963968" type="int64" />\n'
            '</node>\n'
        )
        return str
