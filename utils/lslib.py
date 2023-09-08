import subprocess
import logging
import sys
from typing import Literal
from utils.settings_manager import Paths


class LSLib:
    @staticmethod
    def execute_command(command: Literal["create-package", "extract-package", "convert-resource", "convert-loca"],
                        source_path: str, destination_path: str) -> None:
        try:
            str = [
                Paths.DIVINE_FILE,
                "-g",
                "bg3",
                "-a",
                command,
                "-c",
                "lz4",
                "--source",
                source_path,
                "--destination",
                destination_path,
                "-l",
                "all",
            ]
            subprocess.run(str, check=True)
        except Exception as e:
            logging.error(
                f"An error occurred while executing the lslib command. Reason: {e}")
