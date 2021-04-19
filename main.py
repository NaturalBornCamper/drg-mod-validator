import configparser
import ctypes
import filecmp
import re
from collections import defaultdict
from pathlib import Path
from pprint import pprint
from typing import Dict

from pyrotools.console import cprint, COLORS

import globals
import messages as m
from config import check_config_file, check_config_value, config_get_list
from constants import PREVIOUS_CONTENT_FOLDER_PATH, LATEST_CONTENT_FOLDER_PATH, LATEST, \
    PREVIOUS, MOD_FILE_EXTENSIONS, DEFINITIONS_FOLDER_LOCATION, Mod, MASTER_CONTENT_FOLDERS, \
    VERSION_REGEX, SUPPORTED_PROPERTY_TYPES, SUPPORTED_PROPERTY_TAG_DATA
from property_reader import PropertyReader
from utils import clear_temp_folder, trigger_error, check_valid_folder, get_file_json_counterpart, load_json_from_file, \
    get_mod_name, print_file_result, \
    verify_mod_file, get_corresponding_master_file, confirm


def fetch_master_folders():
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.FETCHING_MASTERS, "=" * 10)
    check_config_value(MASTER_CONTENT_FOLDERS)
    for master_content_folder in config_get_list(globals.settings[MASTER_CONTENT_FOLDERS]):
        master_folder_path = Path(master_content_folder)
        check_valid_folder(master_folder_path)
        # TODO Add version support for experimental u33e.5642
        matches = re.search(pattern=VERSION_REGEX, string=master_content_folder, flags=re.IGNORECASE)
        if not matches:
            trigger_error(m.E_NO_VERSION.format(master_content_folder))
        globals.master_content_folders[matches.group(1)] = master_folder_path
        print(f"Version {matches.group(1)} - {master_content_folder}")

    # pprint(globals.master_content_folders)
    if globals.master_content_folders:
        cprint(COLORS.BRIGHT_CYAN, m.DONE, "\n")
    else:
        trigger_error(m.E_NO_MASTERS.format(globals.settings[MASTER_CONTENT_FOLDERS]))


def load_definition_files():
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.FETCHING_DEFINITIONS, "=" * 10)
    check_config_value(DEFINITIONS_FOLDER_LOCATION)
    check_valid_folder(Path(globals.settings[DEFINITIONS_FOLDER_LOCATION]))
    for definition_file_path in Path(globals.settings[DEFINITIONS_FOLDER_LOCATION]).glob('*.json'):
        print(definition_file_path)
        mod = load_json_from_file(definition_file_path)
        mod[Mod.DEFINITION_FILE_PATH] = definition_file_path
        if Mod.CONTENT_ROOT not in mod:
            trigger_error(m.E_DEFINITION_NO_CONTENT_ROOT.format(definition_file_path, Mod.CONTENT_ROOT))
        elif not Path(mod[Mod.CONTENT_ROOT]).is_dir():
            trigger_error(m.E_DEFINITION_INVALID_CONTENT_ROOT.format(mod[Mod.CONTENT_ROOT], definition_file_path))

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
        trigger_error(m.E_NO_DEFINITIONS.format(globals.settings[DEFINITIONS_FOLDER_LOCATION]))


def __define_all_mods__():
    for mod in globals.mods.values():
        if __define_mod__(mod):
            pprint(mod)
            # Write mod to definition file
            pass


def __define_mod__(mod: Dict):
    content_root = mod[Mod.CONTENT_ROOT]

    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.FETCHING_MODDED_FILES.format(content_root), "=" * 10)
    content_root_path = Path(mod[Mod.CONTENT_ROOT])
    check_valid_folder(content_root_path)

    if mod[Mod.MODDED_FILES]:
        if not confirm(m.W_DEFINITION_HAS_FILES.format(mod[Mod.DEFINITION_FILE_PATH], Mod.MODDED_FILES)):
            cprint(COLORS.BRIGHT_CYAN, m.ABORTED)
            return

    # Find all uexp and uasset files in mod folder
    modded_files_path = [path for path in Path(content_root).rglob('*') if path.suffix in MOD_FILE_EXTENSIONS]
    mod[Mod.MODDED_FILES] = defaultdict(dict)
    for modded_file_path in modded_files_path:
        # Get relative path relative to the content root folder
        modded_file_relative_path = modded_file_path.relative_to(content_root_path)

        # Check file size, if different, mod create with different version than stated
        if not verify_mod_file(mod, modded_file_relative_path, modded_file_path):
            trigger_error(m.E_WRONG_VERSION.format(modded_file_path, mod[Mod.MASTER_VERSION]), False)
            return False

        # Unfortunately, .uasset files not supported at the moment, no idea how the offsets work
        if modded_file_path.suffix == '.uasset': continue
        print(modded_file_path)

        # Make sure modded file has a corresponding master file with the same version as the mod
        master_file_path = get_corresponding_master_file(mod, Path(modded_file_relative_path))

        # Generate json index file (If needed) and load it
        json_index = load_json_from_file(get_file_json_counterpart(master_file_path))

        master_file = open(master_file_path, "rb")
        modded_file = open(content_root_path / modded_file_path, "rb")
        for object_index, object in enumerate(json_index['ExportValues']):
            object_name = object['Object']
            for property_index, property in enumerate(object["Potential Properties"]):
                if 'Type' not in property: continue
                property_type = property['Type']
                # If this property type is not supported, pass it
                if property_type not in SUPPORTED_PROPERTY_TYPES: continue
                # If this property tag data is not supported, pass it
                if 'Tag Data' in property and property['Tag Data']['Name'] not in SUPPORTED_PROPERTY_TAG_DATA: continue

                property_name = property['Property']
                property_offset = property['Value Offset']
                property_size = property['Size']
                master_value = PropertyReader.methods[property_type](master_file, property_offset, property_size)
                modded_value = PropertyReader.methods[property_type](modded_file, property_offset, property_size)

                if master_value != modded_value:
                    key = f"[Object={object_name}][Potential Properties][Property={property_name}]"
                    mod[Mod.MODDED_FILES][modded_file_relative_path.as_posix()][key] = {
                        Mod.OFFSET: key,
                        Mod.ORIGINAL_VALUE: master_value,
                        Mod.MODDED_VALUE: modded_value,
                    }
                    print(f"master_value: {master_value}")
                    print(f"modded_value: {modded_value}")
                    print('')

        master_file.close()
        modded_file.close()
    cprint(COLORS.BRIGHT_CYAN, m.DONE, "\n")
    return True


def __verify_all_mods__():
    for mod in globals.mods.values():
        __verify_mod__(mod)


def __verify_mod__(mod: Dict):
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.VERIFYING_MOD.format(get_mod_name(mod)), "=" * 10)

    # Make sure mod definition has modded files listed
    if Mod.MODDED_FILES not in mod:
        trigger_error(m.E_MOD_NOT_DEFINED_YET.format(mod[Mod.DEFINITION_FILE_PATH]))

    # Make sure mod definition has a DRG Version set
    if Mod.MASTER_VERSION not in mod:
        trigger_error(m.E_NO_MASTER_VERSION_SET.format(mod[Mod.DEFINITION_FILE_PATH], Mod.MASTER_VERSION))

    all_files_ok = True
    for modded_file in mod[Mod.MODDED_FILES]:
        modded_file_relative_path = Path(modded_file)

        modded_file_absolute_path = mod[Mod.CONTENT_ROOT] / modded_file_relative_path
        if verify_mod_file(mod, modded_file_relative_path):
            if globals.settings.getboolean('VERBOSE_OUTPUT', fallback=True):
                print_file_result(modded_file_absolute_path, COLORS.BRIGHT_GREEN, m.FILE_SIZE_OK)
        else:
            all_files_ok = False
            print_file_result(modded_file_absolute_path, COLORS.BRIGHT_YELLOW, m.FILE_SIZE_WRONG)

    if all_files_ok and not globals.settings.getboolean('VERBOSE_OUTPUT', fallback=True):
        cprint(COLORS.BRIGHT_GREEN, m.ALL_FILE_SIZE_OK)

    # pprint(globals.master_files)
    cprint(COLORS.BRIGHT_CYAN, m.DONE, "\n")


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
    content_root = mod[Mod.CONTENT_ROOT]

    clear_temp_folder()

    # Find all uexp and uasset files in mod folder
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, f"Scanning for modded files in {content_root}..", "=" * 10)
    check_valid_folder(mod[Mod.CONTENT_ROOT])

    modded_files = [path for path in Path(content_root).rglob('*') if path.suffix in MOD_FILE_EXTENSIONS]
    for modded_file in modded_files:
        relative_path = str(modded_file.as_posix()).replace(mod[Mod.CONTENT_ROOT], '')

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
    check_config_value(LATEST_CONTENT_FOLDER_PATH)
    check_config_value(PREVIOUS_CONTENT_FOLDER_PATH)
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


if __name__ == "__main__":
    # Activate VT100 console for colors in Windows 10
    kernel32 = ctypes.WinDLL('kernel32')
    hStdOut = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
    mode.value |= 4
    kernel32.SetConsoleMode(hStdOut, mode)

    # Not needed actually
    # globals.temp_folder.mkdir(exist_ok=True)

    check_config_file(configparser.ConfigParser())

    # Run cleanup when program ending (doesn't work when close window however)
    # Not needed actually, no temp folder needed
    # atexit.register(cleanup)

    # Scan all json mod files
    load_definition_files()

    fetch_master_folders()

    __define_all_mods__()

    __verify_all_mods__()

    # ...
    # parse_mod_definitions()

    # # Scan all uexp files in modded content folders
    # scan_modded_files()
    #
    # # Find path to latest original uexp files
    # check_config_value(LATEST_CONTENT_FOLDER_PATH)
    # check_valid_folder(globals.settings[LATEST_CONTENT_FOLDER_PATH])
    # find_modded_files_originals(LATEST_CONTENT_FOLDER_PATH, LATEST)

    while True:
        cprint(COLORS.BRIGHT_MAGENTA, "Choose one of the following options:")
        cprint(COLORS.BRIGHT_MAGENTA, "(V) Validate your mod files")
        cprint(COLORS.BRIGHT_MAGENTA, "(U) Compare updates/hotfixes")
        command = input("Your choice: ").lower()
        if command == "v":
            pass
            # Check modded files for size difference (incompatible)
            # validate_mods()
        elif command == "u":
            # Compare original files between version
            check_latest_update()
        else:
            cprint(COLORS.BRIGHT_RED, "Invalid input")
