import os
import shutil
import logging
import json
from lxml import etree
from typing import List, Dict, Any
from typing import Literal
from utils.enums import FileType


class FileManager:

    # Creates a directory if it doesn't exist
    @staticmethod
    def create_folder(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                logging.debug(f"Created directory {path}")
            except Exception as e:
                logging.error(f"Failed to create directory {path}: {e}")
                return False

    # Deletes all files and folders in the specified folder
    @staticmethod
    def clean_folder(folder_path):
        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        logging.debug(f'Successfully deleted {file_path}')
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        logging.debug(f'Successfully deleted directory {file_path}')
                except Exception as e:
                    logging.error(f'Failed to delete {file_path}. Reason: {e}')
        except Exception as e:
            logging.error(f'Failed to clean folder. Reason: {e}')

    # Searches for files with the specified names in the specified folder
    @staticmethod
    def find_files(folder_path, target_filenames: List[str]):
        found_files = {}
        try:
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if filename in target_filenames:
                        found_files[filename] = os.path.join(root, filename)
                        # logging.debug(f"{filename} path {found_files[filename]}")

        except Exception as e:
            logging.error(f"An error occurred while searching for target files: {e}")

        return found_files

    # Searches for folders with the specified names in the specified folder
    @staticmethod
    def find_folders(folder_path: str, target_folder_names: List[str]) -> Dict[str, str]:
        found_folders = {}
        try:
            for root, dirs, _ in os.walk(folder_path):
                for dir_name in dirs:
                    if dir_name in target_folder_names:
                        found_folders[dir_name] = os.path.join(root, dir_name)
        except Exception as e:
            logging.error(f"An error occurred while searching for target folders: {e}")

        return found_folders
    # Creates a file if it doesn't exist

    @staticmethod
    def create_file(path):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            FileManager.create_folder(directory)  # You can call the create_directory function here

        try:
            with open(path, 'w') as f:
                f.write('')  # Create an empty file
            logging.debug(f"Created file {path}")
        except Exception as e:
            logging.error(f"Failed to create file {path}: {e}")
            return False

    # Writes content to a file
    @staticmethod
    def write_file(path: str, content: str, mode: Literal['a', 'w'] = 'w', insert_at: int = None):
        try:
            if mode == 'a' and insert_at is not None:
                with open(path, 'r+') as f:
                    existing_content = f.read()
                    before = existing_content[:insert_at]
                    after = existing_content[insert_at:]
                    f.seek(0)
                    f.write(before + content + after)
            else:
                with open(path, mode) as f:
                    f.write(content)
            return True
        except Exception as e:
            logging.error(f"Failed to write to file {path} in {mode} mode: {e}")
            return False

    # Saves an object instance to a JSON file
    @staticmethod
    def save_object_to_json(obj, path):
        try:
            with open(path, 'w') as f:
                if isinstance(obj, dict):
                    json.dump(obj, f)
                else:
                    json.dump(obj.__dict__, f)
            logging.info(f"Saved object instance to {path}")
        except Exception as e:
            logging.error(f"Failed to save object instance to {path}: {e}")

    # Loads an object instance from a JSON file
    @staticmethod
    def load_object_from_json(obj, path):
        try:
            with open(path, 'r') as f:
                data = f.read()
                if not data:
                    return {}
                return json.loads(data)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from {path}")
            return {}

    # Writes the specified data to a mod file
    @staticmethod
    def write_mod_file_data(file_type: FileType, obj_list: List[Any], base_string_top=None, base_string_bottom=None):
        obj_string_list = []
        file_contents = ""

        for obj in obj_list:
            obj_string_list.append(obj.__str__(file_type))

        if base_string_top:
            file_contents += f'{"".join(base_string_top)}\n'

        if obj_string_list:
            file_contents += f'{"".join(obj_string_list)}\n'

        if base_string_bottom:
            file_contents += f'{"".join(base_string_bottom)}\n'

        FileManager.write_file(file_type.value, file_contents, 'w')

    # Generates a mod file containing the specified data
    @staticmethod
    def generate_mod_file(file_type: FileType, obj_list: List[Any], base_string_top=None, base_string_bottom=None):
        FileManager.clean_folder(file_type.value)
        FileManager.create_file(file_type.value)
        FileManager.generate_mod_file_data(file_type, obj_list, base_string_top, base_string_bottom)

    # Inserts the specified data after the last node with the specified id in the specified XML file
    @staticmethod
    def insert_after_last_node(xml_file_path, node_id, string_to_insert):
        # Parse the XML file
        tree = etree.parse(xml_file_path)
        root = tree.getroot()

        # Find all nodes with the specified id
        nodes = root.xpath("//node[@id='{}']".format(node_id))

        # If no node with that id is found, return
        if not nodes:
            logging.debug(f"No node with id {node_id} found in {xml_file_path}")
            return

        # Parse the string to insert into an Element object
        new_element = etree.fromstring(string_to_insert)

        # Check if the element already exists
        uuid = new_element.xpath("//attribute[@id='UUID']/@value")
        if uuid:
            existing_nodes = root.xpath("//node[@id='{}']/attribute[@id='UUID' and @value='{}']".format(node_id, uuid[0]))
            if existing_nodes:
                # logging.debug(f"Element with UUID {uuid[0]} already exists. Skipping...")
                return

        # Get the last node
        last_node = nodes[-1]

        # Insert the new element after the last node
        parent = last_node.getparent()
        index = parent.index(last_node)
        parent.insert(index + 1, new_element)

        # Save the modified XML back to the file
        tree.write(xml_file_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    # Converts an XML file to a string
    @staticmethod
    def xml_to_string(xml_file_path):
        try:
            with open(xml_file_path, 'r', encoding='utf-8') as file:
                # remove first line
                # file.readline()
                meta_string = file.read()
            return meta_string
        except Exception as e:
            logging.error(f"Failed to convert XML file to string: {e}")
            return None

    @staticmethod
    def remove_loose_strings_from_xml(file_path):
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(file_path, parser)
            root = tree.getroot()

            def recurse_remove_text(element):
                element.text = None
                element.tail = None
                for child in element:
                    recurse_remove_text(child)

            recurse_remove_text(root)

            with open(file_path, 'wb') as f:
                tree.write(f)
        except Exception as e:
            logging.error(f"An error occurred while removing loose strings from {file_path}: {e}")

    @staticmethod
    def get_file_names(folder_path: str, extension: str):
        return [f for f in os.listdir(folder_path) if f.endswith(f".{extension}")]
