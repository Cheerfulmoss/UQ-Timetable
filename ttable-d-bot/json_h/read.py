import logging
import json
import os

from .write import JsonWriter as jw


class JsonReader:
    def __init__(self):
        """
        Initializes a JsonReader instance.

        This class provides methods for reading JSON files, including error
        handling and clearing content with the help of JsonWriter.
        """
        self._default_logger = logging.getLogger(__name__)

    def extract_from_json_cache(self, file_path: str,
                                logger: logging.Logger = None) -> dict:
        """
        Extracts data from a JSON file, with error handling.

        :param file_path: The path to the JSON file.
            :type: str.
        :param logger: (Optional) The logger to use. If not provided, the
            default logger is used.
            :type: logging.Logger or None.
        :return: The extracted data from the JSON file.
            :rtype: dict.
        """
        logger = logger or self._default_logger
        filename = os.path.basename(file_path)

        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except UnicodeError as e:
            logger.error(f"Unicode error while decoding {filename}: {e}")
        except ValueError as e:
            logger.error(f"Unexpected JSON structure in {filename}: {e}")
        except FileNotFoundError as e:
            logger.error(f"{filename} DNE: {e}")
        except PermissionError as e:
            logger.error(f"Permission error while accessing {filename}: {e}")
        except IsADirectoryError as e:
            logger.error(f"{filename} is a directory, not a file: {e}")
        except IOError as e:
            logger.error(f"I/O error while working with {filename}: {e}")

        jw().clear_json(file_path, logger=logger)
        return {}
