# General
DONE = "DONE"
ABORTED = "ABORTED"
INVALID_INPUT = "Invalid input" + "\n"

# Config/Settings
E_SETTINGS_FILE_NOT_FOUND = "ERROR - No settings.ini found"
E_SETTINGS_SECTION_NOT_FOUND = "ERROR - Section \"SETTINGS\" not found in settings.ini"
E_SETTING_ITEM_NOT_FOUND = "ERROR - \"{}\" not found in settings.ini"
E_SETTING_ITEM_EMPTY = "ERROR - \"{}\" is empty"

# Utils
E_INVALID_FOLDER = "ERROR - \"{}\" is not a valid folder, verify settings.ini file"
E_COUNTERPART_NOT_FOUND = "ERROR - Needed file \"{}\" doesn't exist. Was it deleted?"
E_CANNOT_CREATE_INDEX = "ERROR - Unable to create \"{}\". Check pak'ing command output:"
E_INVALID_JSON_FORMATTING = "ERROR - \"{}\" has invalid json data: {}"
E_JSON_ENCODING_FAILED = "ERROR - Failed to encode json: {}"
E_FAILED_TO_WRITE_MOD_FILE = "ERROR - Failed to write mod to \"{}\": {}"
E_MISSING_MASTER = "ERROR - You don't have master version {} in settings.ini {} needed by \"{}\""
WRONG_FOLDER_STRUCTURE = "\"{}\" has wrong folder structure, searching for it in \"{}\" .."
E_MASTER_FILE_NOT_FOUND = "ERROR - Could not find \"{}\" in \"{}\""
E_INDEX_NOT_FOUND = "NOT FOUND [{}]"

# Menu
AVAILABLE_FUNCTIONS = "Available mod_functions:"
VALIDATE = "(V)alidate your mod files"
DEFINE = "(D)efine mod definition file (existing mod -> definition file) {}"
GENERATE = "(G)enerate mod (definition file -> generate mod)"
COMPARE = "(C)ompare updates/hotfixes"
UPGRADE = "(U)pgrade to last version"
AVAILABLE_MODS = "Available mods:"
INPUT_FUNCTION = "Input function and mod (function + mod number) (ex \"D2\"): "

# fetch_master_folders()
FETCHING_MASTERS = "Scanning for master content folders"
E_NO_VERSION = "ERROR - \"{}\" folder name must contain a version name (ex u34.2)"
E_NO_MASTERS = "ERROR - Settings files \"{}\" doesn't contain any valid folders"

# load_definition_files()
FETCHING_DEFINITIONS = "Scanning for mod definition files"
E_DEFINITION_NO_INPUT_FOLDER = "ERROR - \"{}\" doesn't have a {}"
E_DEFINITION_INVALID_INPUT_FOLDER = "ERROR - \"{}\" in \"{}\" is not a valid folder"
E_NO_DEFINITIONS = "ERROR - \"{}\" doesn't contain any definition files"

# Define
FETCHING_MODDED_FILES = "Scanning for modded files in \'{}\""
W_DEFINITION_HAS_FILES = "WARNING - \"{}\" already has files listed in \"{}\" Overwrite (y/n)? "
E_WRONG_VERSION = "ERROR - \"{}\" size differs from master file, seems like mod was not created from version {}"

# Update
UPDATING_MOD = "Updating mod \"{}\""
E_SAME_VERSION = "ERROR - \"{}\" is already using master version {}, no update needed"
SET_AUTO_VERSION = "Also set mod's \"{}\" to {} (y/n)? "

# Generate
GENERATING_MOD = "Generating mod \"{}\" from definition file"
E_FAILED_CREATE_PAK = "ERROR - pak mod file not created. Check pak'ing command output:"
E_PAK_FILE_WRONG_SIZE = "ERROR - pak mod file has invalid size, something went wrong. Check pak'ing command output:"
E_COMMAND_NOT_FOUND = "ERROR - Command \"{}\" does not exist, check setting \"{}\""

# Verify
VERIFYING_MOD = "Verifying mod \"{}\""
FILE_SIZE_OK = "-> Correct size, game should run"
FILE_SIZE_WRONG = "-> Different size, file needs updating"
ALL_FILE_SIZE_OK = "All modded files have correct size, game should run"
E_MOD_NOT_DEFINED_YET = "ERROR - \"{}\" doesn't have any ModdedFiles yet, try defining it first"
E_NO_MASTER_VERSION_SET = "ERROR - \"{}\" doesn't have a \"{}\" set (ex 34.5)"


