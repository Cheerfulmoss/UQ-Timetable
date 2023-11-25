import logging
import json
import os


def clear_json(logger: logging.Logger, file_path: str):
    with open(file_path, "w") as file:
        json.dump({}, file)
    logger.info(f"{os.path.basename(file_path)} cleared/reset.")


def extract_from_json(logger: logging.Logger, file_path: str):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
    except FileNotFoundError as e:
        logger.error(f"{os.path.basename(file_path)} DNE: {e}")
    clear_json(logger, file_path)
    return {}
