from configparser import ConfigParser

from typing import List

import globals
from utils import trigger_error


def config_get_list(value: str) -> List[str]:
    return list(filter(None, (x.strip() for x in value.splitlines())))


def check_config_file(config_parser: ConfigParser) -> None:
    if not config_parser.read('settings.ini'):
        trigger_error("ERROR - No settings.ini found")

    if 'SETTINGS' not in config_parser:
        trigger_error("ERROR - Section \"SETTINGS\" not found in settings.ini")

    globals.settings = config_parser['SETTINGS']


def check_config_value(item: str) -> None:
    if item not in globals.settings:
        trigger_error(f"ERROR - \"{item}\" not found in settings.ini")
    if not globals.settings[item]:
        trigger_error(f"ERROR - \"{item}\" is empty")
