from pathlib import Path
from typing import Dict

from pyrotools.console import COLORS

import globals
import messages as m
from constants import Mod
from utils import get_mod_name, trigger_error, verify_mod_file, show_message


def all():
    for mod in globals.mods.values():
        one(mod)


def one(mod: Dict):
    show_message(f"{'=' * 10} {m.VERIFYING_MOD.format(get_mod_name(mod))} {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)

    # Make sure mod definition has modded files listed
    if Mod.MODDED_FILES not in mod or not mod[Mod.MODDED_FILES]:
        return trigger_error(m.E_MOD_NOT_DEFINED_YET.format(mod[Mod.DEFINITION_FILE_PATH]), halt=False)

    # Make sure mod definition has a DRG Version set
    if Mod.MASTER_VERSION not in mod:
        return trigger_error(m.E_NO_MASTER_VERSION_SET.format(mod[Mod.DEFINITION_FILE_PATH], Mod.MASTER_VERSION), False)

    all_files_ok = True
    for modded_file in mod[Mod.MODDED_FILES]:
        modded_file_relative_path = Path(modded_file)

        modded_file_absolute_path = mod[Mod.INPUT_FOLDER] / modded_file_relative_path
        if verify_mod_file(mod, modded_file_relative_path):
            show_message(f"{modded_file_absolute_path} {COLORS.BRIGHT_GREEN}{m.FILE_SIZE_OK}")
        else:
            all_files_ok = False
            show_message(f"{modded_file_absolute_path} {COLORS.BRIGHT_YELLOW}{m.FILE_SIZE_WRONG}")

    if all_files_ok:
        show_message(m.ALL_FILE_SIZE_OK, COLORS.BRIGHT_GREEN, important=True)

    show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)
