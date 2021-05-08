from configparser import ConfigParser

from typing import List, Union

from utils import trigger_error

config_parser = ConfigParser()
if not config_parser.read('settings.ini'):
    trigger_error("ERROR - No settings.ini found")

if 'SETTINGS' not in config_parser:
    trigger_error("ERROR - Section \"SETTINGS\" not found in settings.ini")


def check_value(item: str, halt_if_not_found: bool = True, fallback: Union[bool, str] = None) -> bool:
    if item not in config_parser['SETTINGS']:
        if fallback is not None:
            return False
        trigger_error(f"ERROR - \"{item}\" not found in settings.ini", halt=halt_if_not_found)
    if not config_parser['SETTINGS'][item]:
        if fallback is not None:
            return False
        trigger_error(f"ERROR - \"{item}\" is empty", halt=halt_if_not_found)
    return True


def get_string(item: str, halt_if_not_found: bool = True, fallback: str = None) -> str:
    if check_value(item, halt_if_not_found, fallback=fallback):
        return config_parser['SETTINGS'][item]
    else:
        return fallback


def get_boolean(item: str, fallback: bool = None) -> bool:
    if check_value(item, fallback=fallback):
        return config_parser['SETTINGS'].getboolean(item)
    else:
        return fallback


def get_list(item: str) -> List[str]:
    check_value(item)
    return list(filter(None, (x.strip() for x in get_string(item).splitlines())))
