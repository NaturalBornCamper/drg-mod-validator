import json
import msvcrt
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Union

from pyrotools.console import cprint, COLORS

from constants import Mod, JSON_PARSER_PATH, MASTER_CONTENT_FOLDERS
from globals import temp_folder
import globals


def cleanup():
    try:
        temp_folder.rmdir()
    except OSError as e:
        pass


def clear_temp_folder() -> None:
    [f.unlink() for f in temp_folder.iterdir() if f.is_file()]


def trigger_error(message: str, halt: bool = True) -> None:
    cprint(COLORS.BRIGHT_RED, message)
    if halt:
        print('Press any key to exit ...')
        msvcrt.getch()
        sys.exit()


def check_valid_folder(folder: Union[Path, str]) -> None:
    if not Path(folder).is_dir():
        trigger_error("ERROR - \"{}\" is not a valid folder, verify settings.ini file".format(folder))


def get_file_counterpart(path: Path) -> Path:
    if path.suffix == ".uasset":
        return path.with_suffix(".uexp")
    elif path.suffix == ".uexp":
        return path.with_suffix(".uasset")


def get_file_json_counterpart(path: Path) -> Path:
    json_index_path = path.with_name(path.stem + "-UAsset").with_suffix(".json")

    if not json_index_path.is_file():
        # Make sure master_file conterpart exists
        master_file_counterpart_path = get_file_counterpart(path)
        if not master_file_counterpart_path.exists():
            trigger_error(f"ERROR - Needed file \"{master_file_counterpart_path}\" doesn't exist. Was it deleted?")

        subprocess.Popen([globals.settings[JSON_PARSER_PATH], path]).wait()
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


def get_mod_name(mod: Dict) -> str:
    if Mod.NAME in mod:
        return mod[Mod.NAME]
    else:
        return mod[Mod.DEFINITION_FILE_PATH].stem


def print_file_result(filename: Path, color: str, message: str) -> None:
    print("File:", filename, end=' ')
    cprint(color, message)


def verify_mod_file(mod: Dict, modded_file_relative_path: Path, modded_file_path: Path = None):
    # Get corresponding master file and absolute modded file path
    master_file_path = get_corresponding_master_file(mod, modded_file_relative_path)
    if not modded_file_path:
        modded_file_path = Path(mod[Mod.CONTENT_ROOT]) / modded_file_relative_path

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
            for found_file in globals.master_content_folders[current_master_version].rglob(relative_modded_file_path.name):
                current_master_files[relative_modded_file_path.name] = found_file
                break
            if relative_modded_file_path.name not in current_master_files:
                trigger_error("ERROR - Could not find \"{}\" in \"{}\"".format(
                    relative_modded_file_path.name,
                    globals.master_content_folders[current_master_version],
                ))

    return current_master_files[relative_modded_file_path.name]


def confirm(message: str) -> bool:
    answer = input(f"{message} ").lower()
    return answer == 'y'
