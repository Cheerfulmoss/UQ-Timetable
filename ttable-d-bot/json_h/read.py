import logging
import json
import os
import shutil
from datetime import datetime

from .write import JsonWriter as jw


class JsonReader:
    def __init__(self):
        self._default_logger = logging.getLogger(__name__)

    def extract_from_json_cache(self, file_path: str,
                                logger: logging.Logger = None):
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
