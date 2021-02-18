import configparser
import filecmp
import os
import sys
from pathlib import Path
from pprint import pprint

from pyrotools.console import cprint, COLORS, cpprint

from constants import SECTION_GENERAL, MODDED_CONTENT_FOLDER_PATHS, PREVIOUS_CONTENT_FOLDER_PATH, \
    LATEST_CONTENT_FOLDER_PATH, \
    LATEST, PREVIOUS, SECTION_MOD_VALIDATOR, SECTION_UPDATE_ALTERATIONS_MONITOR

unique_modded_files = {}
modded_files = []


def check_config_value(section, item):
    if not config.read('config.ini'):
        sys.exit('ERROR - No config.ini found')

    if section not in config:
        sys.exit('ERROR - Section \"{}\" not found in config.ini'.format(section))

    if item not in config[section]:
        sys.exit('ERROR - \"{}\" not found in config.ini'.format(item))
    if not config[section][item]:
        sys.exit('ERROR - \"{}\" is empty'.format(item))


def verify_config_file():
    check_config_value(SECTION_MOD_VALIDATOR, MODDED_CONTENT_FOLDER_PATHS)
    check_config_value(SECTION_GENERAL, PREVIOUS_CONTENT_FOLDER_PATH)
    check_config_value(SECTION_GENERAL, LATEST_CONTENT_FOLDER_PATH)
    # Check if LATEST_CONTENT_FOLDER_PATH exists
    # Check if PREVIOUS_CONTENT_FOLDER_PATH exists


def scan_modded_files():
    global unique_modded_files, modded_files
    check_config_value(SECTION_MOD_VALIDATOR, MODDED_CONTENT_FOLDER_PATHS)

    # Find all uexp files in modded folders
    cprint(COLORS.BRIGHT_CYAN, "Scanning for modded files..")
    for content_folder_path in get_list(config[SECTION_MOD_VALIDATOR][MODDED_CONTENT_FOLDER_PATHS]):
        for path in Path(content_folder_path).rglob('*.uexp'):
            print(path)
            modded_files.append(path)
            unique_modded_files[path] = {}
    cprint(COLORS.BRIGHT_CYAN, "DONE", "\n")


def find_modded_files_originals(config_section, scan_location, version):
    global unique_modded_files
    cprint(COLORS.CYAN, "Locating modded files in {}, please wait...".format(config[config_section][scan_location]))
    # cprint(COLORS.CYAN, "Locating modded files in {}, please wait... 0%".format(config[config_section][scan_location]))
    total = len(unique_modded_files)
    for index, (file, _) in enumerate(unique_modded_files.items()):
        for found_file in Path(config[config_section][scan_location]).rglob(file.name):
            unique_modded_files[file][version] = found_file
            break
        # if version not in unique_modded_files[file]:
        #     print("not found", end='')
        # cprint(COLORS.BRIGHT_YELLOW, "not found", end='')
        print("{}%".format(index / total * 100))
    # cprint(COLORS.BRIGHT_CYAN, "100%")
    cprint(COLORS.BRIGHT_CYAN, "DONE", "\n")


def validate_mods():
    for modded_file in modded_files:
        pass


def check_latest_update():
    find_modded_files_originals(SECTION_UPDATE_ALTERATIONS_MONITOR, PREVIOUS_CONTENT_FOLDER_PATH, PREVIOUS)

    cprint(COLORS.BRIGHT_CYAN, "Comparing files you need between Ghost Ship Games' updates")
    cprint(COLORS.BRIGHT_CYAN, "Latest version in: {}".format(config[SECTION_GENERAL][LATEST_CONTENT_FOLDER_PATH]))
    cprint(COLORS.BRIGHT_CYAN, "Previous version in: {}".format(
        config[SECTION_UPDATE_ALTERATIONS_MONITOR][PREVIOUS_CONTENT_FOLDER_PATH]
    ))
    for file, paths in unique_modded_files.items():
        print("Current modded file: ", file.name, end='')
        if LATEST not in paths:
            cprint(COLORS.BRIGHT_YELLOW, "Modded file \"{}\" missing from \"{}\", skipping".format(
                file.name,
                config[SECTION_GENERAL][LATEST_CONTENT_FOLDER_PATH]
            ))
        elif PREVIOUS not in paths:
            cprint(COLORS.BRIGHT_YELLOW, "Modded file \"{}\" not found from \"{}\", skipping".format(
                file.name,
                config[SECTION_UPDATE_ALTERATIONS_MONITOR][PREVIOUS_CONTENT_FOLDER_PATH]
            ))
        else:
            cprint(COLORS.BRIGHT_CYAN, file)
            if filecmp.cmp(str(paths[LATEST]), str(paths[PREVIOUS])):
                cprint(COLORS.BRIGHT_GREEN, "-> No change, no update needed")
            else:
                cprint(COLORS.BRIGHT_YELLOW, "-> File has changed, update might be needed")


def get_list(value):
    return list(filter(None, (x.strip() for x in value.splitlines())))


if __name__ == "__main__":
    config = configparser.ConfigParser()

    scan_modded_files()

    # Find path to latest original uexp files
    find_modded_files_originals(SECTION_GENERAL, LATEST_CONTENT_FOLDER_PATH, LATEST)

    # Compare original files between version
    check_latest_update()

    # Check modded files for size difference (incompatible)
    validate_mods()

"""
1-list all uexp modded_files
    Put this file in a list
    also put a unique one in a set, for finding in original later
2-For each unique_modded_file
    find full path in original folder
2-For each unique_modded_file
    check binary content with old and current to see if changed
4-Loop in modded files
    check if size different than latest folder
    
    
"""
