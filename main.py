import ctypes
import filecmp
import msvcrt
import os
import re
import subprocess
from distutils.version import LooseVersion
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Union

from packaging.version import LegacyVersion
from pkg_resources import parse_version
from pyrotools.console import cprint, COLORS

import config
import globals
import messages as m
from constants import LATEST, \
    PREVIOUS, MOD_FILE_EXTENSIONS, DEFINITIONS_FOLDER_LOCATION, Mod, MASTER_CONTENT_FOLDERS, \
    VERSION_REGEX, COMMAND_REGEX, Commands, VERBOSE_OUTPUT, JSON_PARSER_PATH
from mod_functions import define, generate, verify, update
from mod_functions.generate import all
from utils import clear_temp_folder, trigger_error, check_valid_folder, load_json_from_file, \
    get_mod_name, print_file_result, show_message, stdout_to_output
from mod_functions.verify import all


# TODO COMPARE UPDATES
# TODO What happens if a value from a definition file is not in the game files anymore on next update?
# TODO Test mod name with illegal characters like "/" or "?", when writing file name, will it mess up?


def fetch_master_folders():
    show_message(f"{'=' * 10} {m.FETCHING_MASTERS} {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)
    master_content_folders = config.get_list(MASTER_CONTENT_FOLDERS)
    for master_content_folder in master_content_folders:
        master_folder_path = Path(master_content_folder)
        check_valid_folder(master_folder_path)
        matches = re.search(pattern=VERSION_REGEX, string=master_content_folder, flags=re.IGNORECASE)
        if not matches:
            trigger_error(m.E_NO_VERSION.format(master_content_folder))
        globals.master_content_folders[matches.group(1)] = master_folder_path
        show_message(f"Version {matches.group(1)} - {master_content_folder}", important=True)

    # pprint(globals.master_content_folders)
    if globals.master_content_folders:
        show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)
    else:
        trigger_error(m.E_NO_MASTERS.format(MASTER_CONTENT_FOLDERS))

    bob = {}
    # print(globals.master_content_folders.items())
    # print(sorted(globals.master_content_folders.items()))
    # print(dict(sorted(globals.master_content_folders.items())))
    # print(globals.master_content_folders.keys()[-1])
    ordered_versions = list(sorted(globals.master_content_folders, key=LegacyVersion))
    globals.latest_master_version = ordered_versions[-1]
    globals.previous_master_version = ordered_versions[-2] if len(ordered_versions) > 1 else None


def load_definition_files():
    show_message(f"{'=' * 10} {m.FETCHING_DEFINITIONS} {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)
    definitions_folder_path = Path(config.get_string(DEFINITIONS_FOLDER_LOCATION))
    check_valid_folder(definitions_folder_path)
    for definition_file_path in definitions_folder_path.glob('*.json'):
        show_message(definition_file_path, important=True)
        mod = load_json_from_file(definition_file_path)
        mod[Mod.DEFINITION_FILE_PATH] = definition_file_path
        if Mod.INPUT_FOLDER not in mod:
            trigger_error(m.E_DEFINITION_NO_INPUT_FOLDER.format(definition_file_path, Mod.INPUT_FOLDER))
        elif not Path(mod[Mod.INPUT_FOLDER]).is_dir():
            trigger_error(m.E_DEFINITION_INVALID_INPUT_FOLDER.format(mod[Mod.INPUT_FOLDER], definition_file_path))

        # Sanitize modded files location to make sure they don't start with a slash
        if Mod.MODDED_FILES in mod:
            for modded_file_location in dict(mod[Mod.MODDED_FILES]).keys():
                modded_file_path = Path(modded_file_location)
                if modded_file_path.root in ["/", "\\"]:
                    sanitized_modded_file_location = modded_file_path.relative_to("/").as_posix()
                    mod[Mod.MODDED_FILES][sanitized_modded_file_location] = mod[Mod.MODDED_FILES].pop(
                        modded_file_location)

        globals.mods[definition_file_path] = mod

    if globals.mods:
        show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)
    else:
        trigger_error(m.E_NO_DEFINITIONS.format(definitions_folder_path))


def __check_last_update__():
    """
    For each mod:
    1-get master file of every file changed by the mod
    2-get master file of the latest version
    3-Check if bytes are the same
    NOTE: When finding last version, watch out for 33.10 becoming 33.1 as int. Keep as strings
    :return:
    """
    pass


"""
^^^^^^^^^^^^^^^^^^^^^^ GOOD ABOVE ^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^^^^^^^^^^^^^^^^^^^^ GOOD ABOVE ^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^^^^^^^^^^^^^^^^^^^^ GOOD ABOVE ^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^^^^^^^^^^^^^^^^^^^^^ GOOD ABOVE ^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""


def fetch_modded_files(mod):
    # check_config_value(MODDED_CONTENT_FOLDER_PATHS)
    # mod = mods[mod_path]
    input_folder = mod[Mod.INPUT_FOLDER]

    clear_temp_folder()

    # Find all uexp and uasset files in mod folder
    show_message(f"{'=' * 10} Scanning for modded files in {input_folder}.. {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)
    check_valid_folder(mod[Mod.INPUT_FOLDER])

    modded_files = [path for path in Path(input_folder).rglob('*') if path.suffix in MOD_FILE_EXTENSIONS]
    for modded_file in modded_files:
        relative_path = str(modded_file.as_posix()).replace(mod[Mod.INPUT_FOLDER], '')

        add_unique_mod_file(modded_file)

        # COPY ONLY WHEN NEED TO
        copy_to_temp(modded_file)

        # Generate json assets with orginal file
        # bob1 = globals.unique_modded_files[path.name][LATEST]
        # json_asset_path = bob1.with_name(path.stem + '-UAsset').with_suffix('.json')
        # if not json_asset_path.is_file():
        #     subprocess.Popen([globals.settings[JSON_PARSER_PATH], bob1]).wait()
        #
        # globals.original_json = load_json_from_file(json_asset_path)

    show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)


def check_latest_update():
    check_value(LATEST_CONTENT_FOLDER_PATH)
    check_value(PREVIOUS_CONTENT_FOLDER_PATH)
    check_valid_folder(globals.settings[LATEST_CONTENT_FOLDER_PATH])
    check_valid_folder(globals.settings[PREVIOUS_CONTENT_FOLDER_PATH])
    find_modded_file_original(PREVIOUS_CONTENT_FOLDER_PATH, PREVIOUS)

    show_message(f"{'=' * 10} Comparing files you need between hotfixes {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)
    show_message("Latest vanilla version in: \"{}\"".format(globals.settings[LATEST_CONTENT_FOLDER_PATH]))
    show_message(f"Previous vanilla version in: \"{globals.settings[PREVIOUS_CONTENT_FOLDER_PATH]}\"")
    all_files_ok = True
    for filename, paths in globals.unique_modded_files.items():
        if LATEST not in paths:
            print_file_result(
                filename, COLORS.BRIGHT_YELLOW, "-> Modded file \"{}\" missing from \"{}\", skipping".format(
                    filename,
                    globals.settings[LATEST_CONTENT_FOLDER_PATH]
                )
            )
        elif PREVIOUS not in paths:
            print_file_result(
                filename, COLORS.BRIGHT_YELLOW, "-> Modded file \"{}\" missing from \"{}\", skipping".format(
                    filename,
                    globals.settings[PREVIOUS_CONTENT_FOLDER_PATH]
                )
            )
        else:
            if filecmp.cmp(str(paths[LATEST]), str(paths[PREVIOUS])):
                if globals.settings.getboolean('VERBOSE_OUTPUT', fallback=True):
                    print_file_result(filename, COLORS.BRIGHT_GREEN, "-> Files identical, update not needed")
            else:
                all_files_ok = False
                print_file_result(filename, COLORS.BRIGHT_YELLOW, "-> File has changed, should be updated")
    if all_files_ok and not globals.settings.getboolean('VERBOSE_OUTPUT', fallback=True):
        show_message("All files identical, update not needed", COLORS.BRIGHT_GREEN, important=True)
    show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)


all_functions = {
    Commands.DEFINE: define.all,
    Commands.VERIFY: verify.all,
    Commands.GENERATE: generate.all,
    Commands.UPDATE: update.all,
    # Commands.COMPARE: compare.all,
}

single_functions = {
    Commands.DEFINE: define.one,
    Commands.VERIFY: verify.one,
    Commands.GENERATE: generate.one,
    Commands.UPDATE: update.one,
    # Commands.COMPARE: compare.one,
}

if __name__ == "__main__":
    # Activate VT100 console for colors in Windows 10
    kernel32 = ctypes.WinDLL('kernel32')
    hStdOut = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
    mode.value |= 4
    kernel32.SetConsoleMode(hStdOut, mode)

    globals.verbose_output = config.get_boolean(VERBOSE_OUTPUT, fallback=True)

    # Scan all json mod files
    load_definition_files()

    fetch_master_folders()

    first_run_message = f"{COLORS.BRIGHT_RED}(START HERE){COLORS.RESET}"
    while True:
        show_message(m.AVAILABLE_FUNCTIONS, COLORS.BRIGHT_MAGENTA, important=True)
        show_message(m.VALIDATE, COLORS.BRIGHT_BLUE, important=True)
        show_message(m.DEFINE.format(first_run_message), COLORS.BRIGHT_BLUE, important=True)
        show_message(m.GENERATE, COLORS.BRIGHT_BLUE, important=True)
        show_message(m.COMPARE, COLORS.BRIGHT_BLUE, important=True)
        show_message(m.UPGRADE, COLORS.BRIGHT_BLUE, important=True)

        show_message(m.AVAILABLE_MODS, COLORS.BRIGHT_MAGENTA, important=True)
        for count, (key, selected_mod) in enumerate(globals.mods.items(), start=1):
            show_message(f"({count}) {get_mod_name(selected_mod)}", important=True)
        command = input(COLORS.BRIGHT_MAGENTA + m.INPUT_FUNCTION + COLORS.RESET).lower()
        # cprint(COLORS.BRIGHT_MAGENTA, "ex1: \"d1\" = Define mod 1     ex2: \"da\" = Define all mods")

        matches = re.search(pattern=COMMAND_REGEX, string=command, flags=re.IGNORECASE)
        if matches:
            command = matches.group(1)
            parameter = matches.group(2)
            if parameter == "a" and command in all_functions:
                all_functions[command]()
                os.system("pause")
            # TODO Elif below, if d9999 = Index out of range, fix
            elif (mod := list(globals.mods.values())[int(parameter) - 1]) and command in single_functions:
                single_functions[command](mod)
                os.system("pause")
            else:
                show_message(m.INVALID_INPUT, COLORS.BRIGHT_RED, important=True)
        else:
            show_message(m.INVALID_INPUT, COLORS.BRIGHT_RED, important=True)
