from configparser import ConfigParser

from typing import List

from utils import trigger_error

config_parser = ConfigParser()
if not config_parser.read('settings.ini'):
    trigger_error("ERROR - No settings.ini found")

if 'SETTINGS' not in config_parser:
    trigger_error("ERROR - Section \"SETTINGS\" not found in settings.ini")


def check_value(item: str, halt_if_not_found: bool = True) -> None:
    if item not in config_parser['SETTINGS']:
        trigger_error(f"ERROR - \"{item}\" not found in settings.ini", halt=halt_if_not_found)
    if not config_parser['SETTINGS'][item]:
        trigger_error(f"ERROR - \"{item}\" is empty", halt=halt_if_not_found)


def get_string(item: str, halt_if_not_found: bool = True) -> str:
    check_value(item, halt_if_not_found)
    return config_parser['SETTINGS'][item] if item in config_parser['SETTINGS'] else ""


def get_boolean(item: str, fallback: bool = True) -> str:
    check_value(item)
    config_parser['SETTINGS'].getboolean('VERBOSE_OUTPUT', fallback=fallback)
    return config_parser['SETTINGS'][item] if item in config_parser['SETTINGS'] else False


def get_list(item: str) -> List[str]:
    check_value(item)
    return list(filter(None, (x.strip() for x in get_string(item).splitlines())))
