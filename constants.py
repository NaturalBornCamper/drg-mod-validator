# Settings file keys

VERBOSE_OUTPUT = 'VERBOSE_OUTPUT'
DEFINITIONS_FOLDER_LOCATION = 'DEFINITIONS_FOLDER_LOCATION'
MASTER_CONTENT_FOLDERS = 'MASTER_CONTENT_FOLDERS'
JSON_PARSER_PATH = 'JSON_PARSER_PATH'
UNREAL_PACK_COMMAND = 'UNREAL_PACK_COMMAND'
GENERATED_MODS_OUTPUT_FOLDER = 'GENERATED_MODS_OUTPUT_FOLDER'
ZIP_GENERATED_MODS = 'ZIP_GENERATED_MODS'
SET_VERSION_AUTOMATICALLY = 'SET_VERSION_AUTOMATICALLY'

PATH = 'PATH'
LATEST = 'LATEST_VERSION'
PREVIOUS = 'PREVIOUS_VERSION'

MOD_FILE_EXTENSIONS = ['.uexp', '.uasset']

SUPPORTED_PROPERTY_TYPES = ["BoolProperty", "IntProperty", "FloatProperty", "TextProperty", "ArrayProperty", "StructProperty"]

PLUGIN_FILE_EXTENSION = 'uplugin'
COMPILED_PAKS_FOLDER_LOCATION = 'Content/Paks'

VERSION_REGEX = r'u(\d{2}(\.e\d{5})?(\.\d{0,2})?(\.e\d{5})?)'
COMMAND_REGEX = r'^([a-zA-Z])(\d{1,3}|a)$'
KEY_REGEX = r'\[(.+?)\]'

CREATED_BY = 'CREATED_BY'

PAK_FILE_SIZE_MINIMUM = 300


class Mod:
    # Ghost Ship Games indexes
    FILE_VERSION = "FileVersion"
    VERSION_NAME = "VersionName"
    NAME = "FriendlyName"
    DESCRIPTION = "Description"
    CATEGORY = "Category"
    CREATED_BY = "CreatedBy"
    CREATED_BY_URL = "CreatedByURL"

    # Custom indexes
    MASTER_VERSION = "MasterVersion"
    INPUT_FOLDER = "InputFolder"
    MODDED_FILES = "ModdedFiles"

    # Functional indexes not written in file
    DEFINITION_FILE_PATH = "DEFINITION_FILE_PATH"
    OFFSET = "Offset"
    ORIGINAL_VALUE = "OriginalValue"
    MODDED_VALUE = "ModdedValue"


PLUGIN_FILE_KEYS = [
    Mod.FILE_VERSION,
    Mod.VERSION_NAME,
    Mod.NAME,
    Mod.DESCRIPTION,
    Mod.CATEGORY,
    Mod.CREATED_BY,
    Mod.CREATED_BY_URL,
]


DEFINITION_FILE_KEYS = [
    Mod.FILE_VERSION,
    Mod.VERSION_NAME,
    Mod.NAME,
    Mod.DESCRIPTION,
    Mod.CATEGORY,
    Mod.CREATED_BY,
    Mod.CREATED_BY_URL,

    Mod.MASTER_VERSION,
    Mod.INPUT_FOLDER,
    Mod.MODDED_FILES,
]


class Commands:
    DEFINE = 'd'
    VERIFY = 'v'
    GENERATE = 'g'
    COMPARE = 'c'
    UPDATE = 'u'

