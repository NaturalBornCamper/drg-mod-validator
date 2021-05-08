# TODO Add messages from other files (utils, main, etc)

# General
DONE = "DONE"
ABORTED = "ABORTED"
INVALID_INPUT = "Invalid input" + "\n"

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
FAILED_CREATE_PAK = "pak mod file not created. Check pak'ing command output:"
PAK_FILE_WRONG_SIZE = "pak mod file has invalid size, something went wrong. Check pak'ing command output:"

# Verify
VERIFYING_MOD = "Verifying mod \"{}\""
FILE_SIZE_OK = "-> Correct size, game should run"
FILE_SIZE_WRONG = "-> Different size, file needs updating"
ALL_FILE_SIZE_OK = "All modded files have correct size, game should run"
E_MOD_NOT_DEFINED_YET = "ERROR - \"{}\" doesn't have any ModdedFiles yet, try defining it first"
E_NO_MASTER_VERSION_SET = "ERROR - \"{}\" doesn't have a \"{}\" set (ex 34.5)"


