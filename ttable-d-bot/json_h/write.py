import logging
import json
import os
import shutil


class JsonWriter:
    def __init__(self):
        """
        Initializes a JsonWriter instance.

        This class provides methods for managing JSON files, including
        creating backups and clearing content.
        """
        logging.basicConfig(level=logging.INFO,
                            format=LOG_FORMAT)
        self._default_logger = logging.getLogger(__name__)

    def backup_json(self, file_path: str, backup_folder: str = "backup",
                    logger: logging.Logger | None = None) -> None:
        """
        Create a backup of the JSON file.

        :param file_path: The path to the JSON file.
            :type file_path: str.
        :param backup_folder: The folder where backups will be stored.
            Defaults to "backup".
            :type backup_folder: str.
        :param logger: (Optional) The logger to use. If not provided, the
            default logger is used.
            :type logger: logging.Logger or None.
        """
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
                   backup: bool = True) -> None:
        """
        Clear the content of a JSON file.

        Optionally, create a backup before clearing.

        :param file_path: The path to the JSON file.
            :type file_path: str.
        :param logger: (Optional) The logger to use. If not provided, the
            default logger is used.
            :type logger: logging.Logger or None.
        :param backup: (Optional) Whether to create a backup before clearing.
            Defaults to True.
            :type backup: bool.
        """
        if backup:
            self.backup_json(file_path, logger=logger)

        with open(file_path, "w") as file:
            json.dump({}, file)

        logger = logger or self._default_logger
        logger.info(f"{os.path.basename(file_path)} cleared/reset.")

    def write(self, file_path: str, data: dict,
              logger: logging.Logger = None,
              backup: bool = True) -> None:
        """Write to a json file.

        :param file_path: The path to the JSON file.
            :type file_path: str.
        :param data: The data to write to the json file.
            :type data: dict.
        :param logger: (Optional) The logger to use. If not provided, the
            default logger is used.
            :type logger: logging.Logger or None.
        :param backup: (Optional) Whether to create a backup before clearing.
            Defaults to True.
            :type backup: bool.
        """
        logger = logger or self._default_logger

        if backup:
            self.backup_json(file_path, logger=logger)

        with open(file_path, "w") as file:
            json.dump(data, file)
        logger.info(f"Written data to {os.path.basename(file_path)}.")
