import configparser
import ctypes
import filecmp
import msvcrt
import os
import re
import sys
from pathlib import Path

from pyrotools.console import cprint, COLORS

from constants import MODDED_CONTENT_FOLDER_PATHS, PREVIOUS_CONTENT_FOLDER_PATH, LATEST_CONTENT_FOLDER_PATH, LATEST, \
    PREVIOUS, PATH, MOD_FILE_EXTENSIONS

unique_modded_files = {}
modded_files = []
settings = {}


def trigger_error(messsage):
    cprint(COLORS.BRIGHT_RED, messsage)
    print('Press any key to exit ...')
    msvcrt.getch()
    sys.exit()


def config_get_list(value):
    return list(filter(None, (x.strip() for x in value.splitlines())))


def check_config_file():
    if not config.read('settings.ini'):
        trigger_error("ERROR - No settings.ini found")

    if 'SETTINGS' not in config:
        trigger_error("ERROR - Section \"SETTINGS\" not found in settings.ini")


def check_config_value(item):
    if item not in settings:
        trigger_error("ERROR - \"{}\" not found in settings.ini".format(item))
    if not settings[item]:
        trigger_error("ERROR - \"{}\" is empty".format(item))


def check_valid_folder(folder):
    if not os.path.isdir(folder):
        trigger_error("ERROR - \"{}\" is not a valid folder, verify settings.ini file".format(folder))


def print_file_result(filename, color, message):
    print("File:", filename, end=' ')
    cprint(color, message)


def scan_modded_files():
    global unique_modded_files, modded_files
    check_config_value(MODDED_CONTENT_FOLDER_PATHS)

    # Find all uexp files in modded folders
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, "Scanning for modded files..", "=" * 10)
    for content_folder_path in config_get_list(settings[MODDED_CONTENT_FOLDER_PATHS]):
        check_valid_folder(content_folder_path)
        paths = [path for path in Path(content_folder_path).rglob('*') if path.suffix in MOD_FILE_EXTENSIONS]
        for path in paths:
            print(path)
            modded_files.append(path)
            unique_modded_files[path.name] = {PATH: path}
    cprint(COLORS.BRIGHT_CYAN, "DONE", "\n")


def find_modded_files_originals(scan_location, version):
    global unique_modded_files
    check_valid_folder(settings[scan_location])

    cprint(COLORS.CYAN, "=" * 10, f"Locating modded files in {version}, please wait...", "=" * 10)
    # cprint(COLORS.CYAN, "="*10, "Locating modded files in \"{}\", please wait...".format(settings[scan_location]), "="*10)
    # cprint(COLORS.CYAN, "Locating modded files in {}, please wait... 0%".format(settings[scan_location]))
    total = len(unique_modded_files)
    for index, (filename, paths) in enumerate(unique_modded_files.items()):
        # Try to guess the modded file's location in the original content folder
        guessed_location = os.path.join(
            re.split('\\\\Content', settings[scan_location], flags=re.IGNORECASE)[0],
            'Content',
            re.split('content\\\\', str(paths[PATH].absolute()), flags=re.IGNORECASE)[-1]
        )

        # Check if the file is located at the guessed location, or search for it
        if os.path.isfile(guessed_location):
            paths[version] = Path(guessed_location)
        else:
            for found_file in Path(settings[scan_location]).rglob(filename):
                paths[version] = found_file
                break
        # if version not in unique_modded_files[file]:
        #     print("not found", end='')
        # cprint(COLORS.BRIGHT_YELLOW, "not found", end='')
        # print("{}%".format(index / total * 100))
    # cprint(COLORS.BRIGHT_CYAN, "100%")
    cprint(COLORS.BRIGHT_CYAN, "DONE", "\n")


def validate_mods():
    global modded_files, unique_modded_files

    cprint(COLORS.BRIGHT_CYAN, "=" * 10, "Checking your modded files' size against vanilla files", "=" * 10)
    print("Latest vanilla version in: \"{}\"".format(settings[LATEST_CONTENT_FOLDER_PATH]))
    all_files_ok = True
    for modded_file in modded_files:
        if os.path.getsize(modded_file) == os.path.getsize(unique_modded_files[modded_file.name][LATEST]):
            if settings.getboolean('VERBOSE_OUTPUT', fallback=True):
                print_file_result(modded_file.absolute(), COLORS.BRIGHT_GREEN, "-> Correct size, game should run")
        else:
            all_files_ok = False
            print_file_result(modded_file.absolute(), COLORS.BRIGHT_YELLOW, "-> Different size, game will not run")

    if all_files_ok and not settings.getboolean('VERBOSE_OUTPUT', fallback=True):
        cprint(COLORS.BRIGHT_GREEN, "All files have correct size, game should run")
    cprint(COLORS.BRIGHT_CYAN, "DONE", "\n")


def check_latest_update():
    check_config_value(LATEST_CONTENT_FOLDER_PATH)
    check_config_value(PREVIOUS_CONTENT_FOLDER_PATH)
    check_valid_folder(settings[LATEST_CONTENT_FOLDER_PATH])
    check_valid_folder(settings[PREVIOUS_CONTENT_FOLDER_PATH])
    find_modded_files_originals(PREVIOUS_CONTENT_FOLDER_PATH, PREVIOUS)

    cprint(COLORS.BRIGHT_CYAN, "=" * 10, "Comparing files you need between hotfixes", "=" * 10)
    print("Latest vanilla version in: \"{}\"".format(settings[LATEST_CONTENT_FOLDER_PATH]))
    print(f"Previous vanilla version in: \"{settings[PREVIOUS_CONTENT_FOLDER_PATH]}\"")
    all_files_ok = True
    for filename, paths in unique_modded_files.items():
        if LATEST not in paths:
            print_file_result(
                filename, COLORS.BRIGHT_YELLOW, "-> Modded file \"{}\" missing from \"{}\", skipping".format(
                    filename,
                    settings[LATEST_CONTENT_FOLDER_PATH]
                )
            )
        elif PREVIOUS not in paths:
            print_file_result(
                filename, COLORS.BRIGHT_YELLOW, "-> Modded file \"{}\" missing from \"{}\", skipping".format(
                    filename,
                    settings[PREVIOUS_CONTENT_FOLDER_PATH]
                )
            )
        else:
            if filecmp.cmp(str(paths[LATEST]), str(paths[PREVIOUS])):
                if settings.getboolean('VERBOSE_OUTPUT', fallback=True):
                    print_file_result(filename, COLORS.BRIGHT_GREEN, "-> Files identical, update not needed")
            else:
                all_files_ok = False
                print_file_result(filename, COLORS.BRIGHT_YELLOW, "-> File has changed, should be updated")
    if all_files_ok and not settings.getboolean('VERBOSE_OUTPUT', fallback=True):
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

    config = configparser.ConfigParser()
    check_config_file()
    settings = config['SETTINGS']

    # Scan all uexp files in modded content folders
    scan_modded_files()

    # Find path to latest original uexp files
    check_config_value(LATEST_CONTENT_FOLDER_PATH)
    check_valid_folder(settings[LATEST_CONTENT_FOLDER_PATH])
    find_modded_files_originals(LATEST_CONTENT_FOLDER_PATH, LATEST)

    while True:
        cprint(COLORS.BRIGHT_MAGENTA, "Choose one of the following options:")
        cprint(COLORS.BRIGHT_MAGENTA, "(V) Validate your mod files")
        cprint(COLORS.BRIGHT_MAGENTA, "(U) Compare updates/hotfixes")
        command = input("Your choice: ").lower()
        if command == "v":
            # Check modded files for size difference (incompatible)
            validate_mods()
        elif command == "u":
            # Compare original files between version
            check_latest_update()
        else:
            cprint(COLORS.BRIGHT_RED, "Invalid input")
