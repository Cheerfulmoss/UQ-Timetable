import logging
import json
import os
import shutil
from datetime import datetime


class JsonWriter:
    def __init__(self):
        self._default_logger = logging.getLogger(__name__)

    def backup_json(self, file_path: str, backup_folder: str = "backup",
                    logger: logging.Logger = None):
        logger = logger or self._default_logger

        if not os.path.exists(backup_folder):
            logger.warning(f"Backup folder '{backup_folder}' does not "
                           f"exist... Creating folder '{backup_folder}'")
            os.makedirs(backup_folder)

        filename = os.path.basename(file_path)
        backup_file_path = os.path.join(backup_folder,
                                        f"{filename}.bak")

        try:
            shutil.copyfile(file_path, backup_file_path)
            logger.info(f"Backup created: {backup_file_path}")
        except Exception as e:
            logger.error(f"Error creating backup: {e}")

    def clear_json(self, file_path: str,
                   logger: logging.Logger = None,
                   backup: bool = True):
        if backup:
            self.backup_json(file_path, logger=logger)

        with open(file_path, "w") as file:
            json.dump({}, file)

        logger = logger or self._default_logger
        logger.info(f"{os.path.basename(file_path)} cleared/reset.")
