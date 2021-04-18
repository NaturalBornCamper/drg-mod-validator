import json
import msvcrt
import os
import sys
from pathlib import Path
from typing import Dict

from pyrotools.console import cprint, COLORS

from constants import Mod
from globals import temp_folder
import globals


def cleanup():
    try:
        temp_folder.rmdir()
    except OSError as e:
        pass


def clear_temp_folder() -> None:
    [f.unlink() for f in temp_folder.iterdir() if f.is_file()]


def trigger_error(message: str) -> None:
    cprint(COLORS.BRIGHT_RED, message)
    print('Press any key to exit ...')
    msvcrt.getch()
    sys.exit()


def check_valid_folder(folder: Path) -> None:
    # if not os.path.isdir(folder):
    if not folder.is_dir():
        trigger_error("ERROR - \"{}\" is not a valid folder, verify settings.ini file".format(folder))


def get_file_counterpart(path: Path) -> Path:
    if path.suffix == ".uasset":
        return path.with_suffix(".uexp")
    elif path.suffix == ".uexp":
        return path.with_suffix(".uasset")


def get_file_counterpart_json(path: Path) -> Path:
    return path.with_name(path.stem + "-UAsset").with_suffix(".json")


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
