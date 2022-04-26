from typing import Dict

from pyrotools.console import COLORS

import config
import globals
import messages as m
from constants import Mod, SET_VERSION_AUTOMATICALLY
from mod_functions import generate
from utils import get_mod_name, trigger_error, confirm, show_message, \
    trigger_warning


def all():
    for mod in globals.mods.values():
        one(mod)


def one(mod: Dict):
    mod_name = get_mod_name(mod)
    show_message(f"{'=' * 10} {m.UPDATING_MOD.format(mod_name)} {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)

    if Mod.MODDED_FILES not in mod or not mod[Mod.MODDED_FILES]:
        return trigger_error(m.E_MOD_NOT_DEFINED_YET.format(mod[Mod.DEFINITION_FILE_PATH]), halt=False)

    if mod[Mod.MASTER_VERSION] == globals.latest_master_version:
        return trigger_warning(m.E_SAME_VERSION.format(mod_name, globals.latest_master_version), halt=False)

    mod[Mod.MASTER_VERSION] = globals.latest_master_version

    new_version_name = f"{globals.latest_master_version}.0"
    if config.check_value_set(SET_VERSION_AUTOMATICALLY):
        if config.get_boolean(SET_VERSION_AUTOMATICALLY):
            mod[Mod.VERSION_NAME] = new_version_name
    elif confirm(m.SET_AUTO_VERSION.format(Mod.VERSION_NAME, new_version_name)):
        mod[Mod.VERSION_NAME] = new_version_name

    show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)
    generate.one(mod)
