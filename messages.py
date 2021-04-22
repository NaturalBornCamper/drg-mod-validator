# TODO Add messages from other files (utils, main, etc)

# General
DONE = "DONE"
ABORTED = "ABORTED"
INVALID_INPUT = "Invalid input" + "\n"

# fetch_master_folders()
FETCHING_MASTERS = "Scanning for master content folders.."
E_NO_VERSION = "ERROR - \"{}\" folder name must contain a version name (ex u34.2)"
E_NO_MASTERS = "ERROR - Settings files \"{}\" doesn't contain any valid folders"

# load_definition_files()
FETCHING_DEFINITIONS = "Scanning for mod definition files.."
E_DEFINITION_NO_CONTENT_ROOT = "ERROR - \"{}\" doesn't have a {}"
E_DEFINITION_INVALID_CONTENT_ROOT = "ERROR - \"{}\" in \"{}\" is not a valid folder"
E_NO_DEFINITIONS = "ERROR - \"{}\" doesn't contain any definition files"

# __define_mod__()
FETCHING_MODDED_FILES = "Scanning for modded files in {}.."
W_DEFINITION_HAS_FILES = "WARNING - \"{}\" already has files listed in \"{}\" Overwrite? "
E_WRONG_VERSION = "ERROR - \"{}\" size differs from master file, seems like mod was not created from version {}"

# __generate_mod__()
GENERATING_MOD = "Generating mod \"{}\" from definition file.."

# __verify_mod__()
VERIFYING_MOD = "Verifying mod \"{}\".."
FILE_SIZE_OK = "-> Correct size, game should run"
FILE_SIZE_WRONG = "-> Different size, file needs updating"
ALL_FILE_SIZE_OK = "All modded files have correct size, game should run"
E_MOD_NOT_DEFINED_YET = "ERROR - \"{}\" doesn't have any ModdedFiles yet, try defining it first"
E_NO_MASTER_VERSION_SET = "ERROR - \"{}\" doesn't have a \"{}\" set (ex 34.5)"


