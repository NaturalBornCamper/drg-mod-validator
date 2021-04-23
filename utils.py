import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from pyclbr import Class
from typing import Dict, Union, List

from pyrotools.console import cprint, COLORS

import config
from constants import Mod, JSON_PARSER_PATH, MASTER_CONTENT_FOLDERS, DEFINITION_FILE_KEYS, CREATED_BY, \
    PLUGIN_FILE_EXTENSION
from globals import temp_folder
import globals


# TODO show_message(message, color) that will check if verbose is activated


def clear_temp_folder() -> None:
    [f.unlink() for f in temp_folder.iterdir() if f.is_file()]


# TODO Cleanup before ending (Only if halt and cleanup setting is true)
def trigger_error(message: str, halt: bool = True) -> None:
    cprint(COLORS.BRIGHT_RED, message)
    if halt:
        os.system("pause")
        sys.exit()


def check_valid_folder(folder: Union[Path, str]) -> None:
    if not Path(folder).is_dir():
        trigger_error("ERROR - \"{}\" is not a valid folder, verify settings.ini file".format(folder))


def get_file_counterpart(path: Path) -> Path:
    if path.suffix == ".uasset":
        return path.with_suffix(".uexp")
    elif path.suffix == ".uexp":
        return path.with_suffix(".uasset")


# Returns file's json counterpart path if exist, or generate it if not
def get_file_json_counterpart(path: Path) -> Path:
    json_index_path = path.with_name(path.stem + "-UAsset").with_suffix(".json")

    if not json_index_path.is_file():
        # Make sure master_file conterpart exists
        master_file_counterpart_path = get_file_counterpart(path)
        if not master_file_counterpart_path.exists():
            trigger_error(f"ERROR - Needed file \"{master_file_counterpart_path}\" doesn't exist. Was it deleted?")

        # TODO Detect if error when there is output, or maybe command returns a code, like 0 = no error?
        subprocess.Popen([config.get_string(JSON_PARSER_PATH), path]).wait()
        if not json_index_path.is_file():
            trigger_error(
                "ERROR - Unable to create \"{}\", try running the parser manually and see if you get errors".format(
                    json_index_path
                )
            )
    return json_index_path


def load_json_from_file(file_path: Path) -> Dict:
    with open(file_path) as file:
        try:
            json_data = json.load(file)
        except ValueError as e:
            trigger_error(f"ERROR - \"{file_path}\" has invalid json data: {e}")

    return json_data


def write_mod_details_to_file(mod: Dict, destination_file_path: Path = None, keys: List = DEFINITION_FILE_KEYS) -> bool:
    if not destination_file_path:
        destination_file_path = mod[Mod.DEFINITION_FILE_PATH]

    data = {}
    for key in keys:
        if key in mod:
            data[key] = mod[key]
        else:
            data[key] = ""

    if not data[Mod.VERSION_NAME]:
        data[Mod.VERSION_NAME] = mod[Mod.MASTER_VERSION] + ".0"

    if not data[Mod.NAME]:
        data[Mod.NAME] = destination_file_path.stem

    if not data[Mod.CREATED_BY]:
        data[Mod.CREATED_BY] = config.get_string(CREATED_BY)

    # TODO Remove from definition file maybe? Or save it in definition file after generating
    if destination_file_path.suffix == f".{PLUGIN_FILE_EXTENSION}":
        data[Mod.FILE_VERSION] = (int(data[Mod.FILE_VERSION]) if data[Mod.FILE_VERSION] else 0) + 1

    try:
        json.dumps(data, ensure_ascii=False, indent=4)
    except Exception as e:
        trigger_error(f"ERROR - Failed to make json: {e}")
        return False

    with open(destination_file_path, 'w', encoding='utf-8') as definition_file:
        try:
            json.dump(data, definition_file, ensure_ascii=False, indent=4)
        except Exception as e:
            trigger_error(f"ERROR - Failed to write mod to \"{destination_file_path}\": {e}")

    return True


def get_mod_name(mod: Dict) -> str:
    if Mod.NAME in mod:
        return mod[Mod.NAME]
    else:
        return mod[Mod.DEFINITION_FILE_PATH].stem


def print_file_result(filename: Path, color: str, message: str) -> None:
    print("File:", filename, end=' ')
    cprint(color, message)


# Check modded file size compared to master file size
def verify_mod_file(mod: Dict, modded_file_relative_path: Path, modded_file_path: Path = None):
    # Get corresponding master file and absolute modded file path
    master_file_path = get_corresponding_master_file(mod, modded_file_relative_path)
    if not modded_file_path:
        modded_file_path = Path(mod[Mod.INPUT_FOLDER]) / modded_file_relative_path

    # Compare master file's size with modded file's size
    return os.path.getsize(master_file_path) == os.path.getsize(modded_file_path)


def get_corresponding_master_file(mod: Dict, relative_modded_file_path: Path) -> Path:
    current_master_version = mod[Mod.MASTER_VERSION]
    if current_master_version not in globals.master_content_folders:
        trigger_error("ERROR - You don't have version {} in settings.ini {} needed by \"{}\"".format(
            current_master_version,
            MASTER_CONTENT_FOLDERS,
            mod[Mod.DEFINITION_FILE_PATH]
        ))

    # Create dictionary for that master version if if doesn't exist yet
    if current_master_version not in globals.master_files:
        globals.master_files[current_master_version] = {}

    current_master_files = globals.master_files[current_master_version]
    # Check if that master file was already located
    if relative_modded_file_path.name in current_master_files:
        return current_master_files[relative_modded_file_path.name]
    else:
        # Try to guess the modded file's location in the original content folder from expected hierarchy
        guessed_location = globals.master_content_folders[current_master_version].parent / relative_modded_file_path

        # Check if the file is located at the guessed location, or search for it
        if guessed_location.is_file():
            current_master_files[relative_modded_file_path.name] = guessed_location
        else:
            cprint(COLORS.BRIGHT_CYAN, "\"{}\" has wrong folder structure, searching for it in \"{}\" ..".format(
                relative_modded_file_path.name,
                globals.master_content_folders[current_master_version]
            ))
            for found_file in globals.master_content_folders[current_master_version].rglob(
                    relative_modded_file_path.name):
                current_master_files[relative_modded_file_path.name] = found_file
                break
            if relative_modded_file_path.name not in current_master_files:
                trigger_error("ERROR - Could not find \"{}\" in \"{}\"".format(
                    relative_modded_file_path.name,
                    globals.master_content_folders[current_master_version],
                ))

    return current_master_files[relative_modded_file_path.name]


def confirm(message: str) -> bool:
    # cprint(COLORS.BRIGHT_YELLOW, message)
    answer = input(COLORS.BRIGHT_YELLOW + message + COLORS.RESET).lower()
    return answer == 'y'


def recursive_search(data: Union[List, Dict], queries: List):
    query = queries.pop(0)

    if '=' in query:  # LIST OF DICTIONARIES = loop in values until we find the one
        key, value = query.split(sep="=")
        for dictionary in data:
            if key in dictionary and dictionary[key] == value:
                if len(queries):
                    return recursive_search(dictionary, queries)
                else:
                    return dictionary
        trigger_error(f"NOT FOUND [{query}]")
    else:  # DICTIONARY = direct access
        if len(queries):
            return recursive_search(data[query], queries)
        else:
            return data[query]


def cmd_exists(cmd):
    return shutil.which(cmd) is not None

