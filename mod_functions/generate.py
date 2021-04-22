from pathlib import Path
from typing import Dict

from pyrotools.console import cprint, COLORS

import config
import globals
import messages as m
from constants import GENERATED_MODS_OUTPUT_FOLDER, Mod
from utils import get_mod_name, check_valid_folder, trigger_error, get_corresponding_master_file, load_json_from_file, \
    get_file_json_counterpart


def all():
    for mod in globals.mods.values():
        one(mod)


# TODO FileVersion is increased in define() but maybe it should be in generate?
def one(mod: Dict):
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.GENERATING_MOD.format(get_mod_name(mod)), "=" * 10)
    check_valid_folder(config.get_string(GENERATED_MODS_OUTPUT_FOLDER))

    if Mod.MODDED_FILES not in mod or not mod[Mod.MODDED_FILES]:
        return trigger_error(m.E_MOD_NOT_DEFINED_YET.format(mod[Mod.DEFINITION_FILE_PATH]), halt=False)

    for modded_file_relative_location, file_changes in mod[Mod.MODDED_FILES].items():
        # Get corresponding master file and absolute modded file path
        master_file_path = get_corresponding_master_file(mod, Path(modded_file_relative_location))

        # Generate json index file (If needed) and load it
        json_index = load_json_from_file(get_file_json_counterpart(master_file_path))

        # Get relative path relative to the content root folder
        modded_file_relative_path = modded_file_path.relative_to(content_root_path)
        master_file = open(master_file_path, "rb")

        for key, changes in file_changes.items():
            print(key)
            print(changes[Mod.ORIGINAL_VALUE])
            print(changes[Mod.MODDED_VALUE])

    cprint(COLORS.BRIGHT_CYAN, m.DONE, "\n")


