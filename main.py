import ctypes
import filecmp
import msvcrt
import os
import re
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Union

from pyrotools.console import cprint, COLORS

import config
import globals
import messages as m
from constants import LATEST, \
    PREVIOUS, MOD_FILE_EXTENSIONS, DEFINITIONS_FOLDER_LOCATION, Mod, MASTER_CONTENT_FOLDERS, \
    VERSION_REGEX, COMMAND_REGEX, Commands
from mod_functions import define, generate, verify
from mod_functions.generate import all
from utils import clear_temp_folder, trigger_error, check_valid_folder, load_json_from_file, \
    get_mod_name, print_file_result
from mod_functions.verify import all

# TODO Check with umodel if folder hieararchy inside pak file is the same when config.txt doesn't have "../../FSD"
# TODO What happens if a value from a definition file is not in the game files anymore on next update?
# TODO Test mod name with illegal characters like "/" or "?", when writing file name, will it mess up?
# TODO definition file, contentRoot = "Folder containing the "Content" folder "InputFolder"?


def fetch_master_folders():
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.FETCHING_MASTERS, "=" * 10)
    master_content_folders = config.get_list(MASTER_CONTENT_FOLDERS)
    for master_content_folder in master_content_folders:
        master_folder_path = Path(master_content_folder)
        check_valid_folder(master_folder_path)
        matches = re.search(pattern=VERSION_REGEX, string=master_content_folder, flags=re.IGNORECASE)
        if not matches:
            trigger_error(m.E_NO_VERSION.format(master_content_folder))
        globals.master_content_folders[matches.group(1)] = master_folder_path
        print(f"Version {matches.group(1)} - {master_content_folder}")

    # pprint(globals.master_content_folders)
    if globals.master_content_folders:
        cprint(COLORS.BRIGHT_CYAN, m.DONE, "\n")
    else:
        trigger_error(m.E_NO_MASTERS.format(MASTER_CONTENT_FOLDERS))


def load_definition_files():
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.FETCHING_DEFINITIONS, "=" * 10)
    definitions_folder_path = Path(config.get_string(DEFINITIONS_FOLDER_LOCATION))
    check_valid_folder(definitions_folder_path)
    for definition_file_path in definitions_folder_path.glob('*.json'):
        print(definition_file_path)
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
        cprint(COLORS.BRIGHT_CYAN, m.DONE, "\n")
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
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, f"Scanning for modded files in {input_folder}..", "=" * 10)
    check_valid_folder(mod[Mod.INPUT_FOLDER])

    modded_files = [path for path in Path(input_folder).rglob('*') if path.suffix in MOD_FILE_EXTENSIONS]
    for modded_file in modded_files:
        relative_path = str(modded_file.as_posix()).replace(mod[Mod.INPUT_FOLDER], '')

        add_unique_mod_file(modded_file)

        # COPY ONLY WHEN NEED TO
        copy_to_temp(modded_file)

        # # New modded file that was not in the definition file before
        # if relative_path not in mod[Mod.MODDED_FILES]:
        #     mod[Mod.MODDED_FILES][relative_path] = {}
        #     # TODO Also check if modded file has same size as original to see if it can be parsed
        #     # TODO Or.. Compare json index files and see if they are different
        # modded_files.append(path)

        # Generate json assets with orginal file
        # bob1 = globals.unique_modded_files[path.name][LATEST]
        # json_asset_path = bob1.with_name(path.stem + '-UAsset').with_suffix('.json')
        # if not json_asset_path.is_file():
        #     subprocess.Popen([globals.settings[JSON_PARSER_PATH], bob1]).wait()
        #
        # globals.original_json = load_json_from_file(json_asset_path)

    cprint(COLORS.BRIGHT_CYAN, "DONE", "\n")


def check_latest_update():
    check_value(LATEST_CONTENT_FOLDER_PATH)
    check_value(PREVIOUS_CONTENT_FOLDER_PATH)
    check_valid_folder(globals.settings[LATEST_CONTENT_FOLDER_PATH])
    check_valid_folder(globals.settings[PREVIOUS_CONTENT_FOLDER_PATH])
    find_modded_file_original(PREVIOUS_CONTENT_FOLDER_PATH, PREVIOUS)

    cprint(COLORS.BRIGHT_CYAN, "=" * 10, "Comparing files you need between hotfixes", "=" * 10)
    print("Latest vanilla version in: \"{}\"".format(globals.settings[LATEST_CONTENT_FOLDER_PATH]))
    print(f"Previous vanilla version in: \"{globals.settings[PREVIOUS_CONTENT_FOLDER_PATH]}\"")
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
        cprint(COLORS.BRIGHT_GREEN, "All files identical, update not needed")
    cprint(COLORS.BRIGHT_CYAN, "DONE", "\n")


all_functions = {
    Commands.DEFINE: define.all,
    Commands.VERIFY: verify.all,
    Commands.GENERATE: generate.all,
    # Commands.COMPARE: compare.all,
}

single_functions = {
    Commands.DEFINE: define.one,
    Commands.VERIFY: verify.one,
    Commands.GENERATE: generate.one,
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

    # Scan all json mod files
    load_definition_files()

    fetch_master_folders()

    # # Scan all uexp files in modded content folders
    # scan_modded_files()
    #
    # # Find path to latest original uexp files
    # check_config_value(LATEST_CONTENT_FOLDER_PATH)
    # check_valid_folder(globals.settings[LATEST_CONTENT_FOLDER_PATH])
    # find_modded_files_originals(LATEST_CONTENT_FOLDER_PATH, LATEST)

    first_run_message = f"{COLORS.BRIGHT_RED}(START HERE){COLORS.RESET}"
    while True:
        cprint(COLORS.BRIGHT_MAGENTA, "Available mod_functions:")
        cprint(COLORS.BRIGHT_BLUE, "(V)alidate your mod files")
        cprint(COLORS.BRIGHT_BLUE, "(D)efine mod definition file (existing mod -> definition file)", first_run_message)
        cprint(COLORS.BRIGHT_BLUE, "(G)enerate mod (definition file -> generate mod)")
        cprint(COLORS.BRIGHT_BLUE, "(C)ompare updates/hotfixes")  # TODO When looking for last version, the "e" in experimental might mess up order, find best way of writing exp branch
        cprint(COLORS.BRIGHT_BLUE, "(U)pgrade to last version")

        cprint(COLORS.BRIGHT_MAGENTA, "Available mods:")
        for count, (key, selected_mod) in enumerate(globals.mods.items(), start=1):
            print(f"({count}) {get_mod_name(selected_mod)}")
        command = input(
            COLORS.BRIGHT_MAGENTA + "Input function and mod (function + mod number) (ex \"D2\"): " + COLORS.RESET
        ).lower()
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
                cprint(COLORS.BRIGHT_RED, m.INVALID_INPUT)
        else:
            cprint(COLORS.BRIGHT_RED, m.INVALID_INPUT)
