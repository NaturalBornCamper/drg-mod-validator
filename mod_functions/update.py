import re
import shutil
import subprocess
from pathlib import Path
from pprint import pprint
from typing import Dict
from zipfile import ZipFile

from pyrotools.console import cprint, COLORS

import config
import globals
import messages as m
from constants import GENERATED_MODS_OUTPUT_FOLDER, Mod, PLUGIN_FILE_KEYS, KEY_REGEX, SUPPORTED_PROPERTY_TYPES, \
    UNREAL_PACK_COMMAND, PLUGIN_FILE_EXTENSION, COMPILED_PAKS_FOLDER_LOCATION, SET_VERSION_AUTOMATICALLY
from mod_functions import generate
from hex import PropertyWriter
from utils import get_mod_name, check_valid_folder, trigger_error, get_corresponding_master_file, load_json_from_file, \
    get_json_index_filepath, write_mod_details_to_file, recursive_search, cmd_exists, confirm, show_message


def all():
    for mod in globals.mods.values():
        one(mod)


def one(mod: Dict):
    mod_name = get_mod_name(mod)
    show_message(f"{'=' * 10} {m.UPDATING_MOD.format(mod_name)} {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)

    if Mod.MODDED_FILES not in mod or not mod[Mod.MODDED_FILES]:
        return trigger_error(m.E_MOD_NOT_DEFINED_YET.format(mod[Mod.DEFINITION_FILE_PATH]), halt=False)

    if mod[Mod.MASTER_VERSION] == globals.latest_master_version:
        return trigger_error(m.E_SAME_VERSION.format(mod_name, globals.latest_master_version), halt=False)

    mod[Mod.MASTER_VERSION] = globals.latest_master_version

    new_version_name = f"{globals.latest_master_version}.0"
    if config.check_value_set(SET_VERSION_AUTOMATICALLY):
        if config.get_boolean(SET_VERSION_AUTOMATICALLY):
            mod[Mod.VERSION_NAME] = new_version_name
    elif confirm(m.SET_AUTO_VERSION.format(Mod.VERSION_NAME, new_version_name)):
        mod[Mod.VERSION_NAME] = new_version_name

    show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)
    generate.one(mod)
