from collections import defaultdict
from pathlib import Path
from typing import Dict

from pyrotools.console import cprint, COLORS

import globals
import messages as m
from constants import Mod, MOD_FILE_EXTENSIONS, SUPPORTED_PROPERTY_TYPES
from hex import PropertyReader
from utils import check_valid_folder, confirm, verify_mod_file, trigger_error, get_corresponding_master_file, \
    load_json_from_file, get_json_index_filepath, write_mod_details_to_file, show_message


def all():
    for mod in globals.mods.values():
        one(mod)


def one(mod: Dict):
    input_folder_path = Path(mod[Mod.INPUT_FOLDER])
    show_message(f"{'=' * 10} {m.FETCHING_MODDED_FILES.format(input_folder_path)} {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)
    check_valid_folder(input_folder_path)

    # Confirm overwrite
    if Mod.MODDED_FILES in mod and mod[Mod.MODDED_FILES]:
        if not confirm(m.W_DEFINITION_HAS_FILES.format(mod[Mod.DEFINITION_FILE_PATH], Mod.MODDED_FILES)):
            show_message(m.ABORTED, COLORS.BRIGHT_CYAN, important=True)
            return

    # Find all uexp and uasset files in mod folder
    modded_files_path = [path for path in Path(input_folder_path).rglob('*') if path.suffix in MOD_FILE_EXTENSIONS]
    mod[Mod.MODDED_FILES] = defaultdict(dict)
    for modded_file_path in modded_files_path:
        # Get relative path relative to the content root folder
        modded_file_relative_path = modded_file_path.relative_to(input_folder_path)

        # Check file size, if different, mod create with different version than stated
        if not verify_mod_file(mod, modded_file_relative_path, modded_file_path):
            trigger_error(m.E_WRONG_VERSION.format(modded_file_path, mod[Mod.MASTER_VERSION]), False)
            return False

        # Unfortunately, .uasset files not supported at the moment, no idea how the offsets work
        if modded_file_path.suffix == '.uasset':
            mod[Mod.MODDED_FILES][modded_file_relative_path.as_posix()] = {}
            continue
        show_message(modded_file_path)

        # Make sure modded file has a corresponding master file with the same version as the mod
        master_file_path = get_corresponding_master_file(mod, Path(modded_file_relative_path))

        # Generate json index file (If needed) and load it
        if not (json_index := load_json_from_file(get_json_index_filepath(master_file_path))):
            return False

        master_file = open(master_file_path, "rb")
        modded_file = open(modded_file_path, "rb")
        for object_index, object in enumerate(json_index['ExportValues']):
            object_name = object['Object']
            for property_index, property in enumerate(object["Potential Properties"]):
                if 'Type' not in property:
                    continue

                property_type = property['Type']
                # If this property type is not supported, pass it
                if property_type not in SUPPORTED_PROPERTY_TYPES:
                    continue

                # print(f"KEY --> [Object={object_name}][Potential Properties][Property={property['Property']}]")
                master_value = PropertyReader.methods[property_type](master_file, property)
                modded_value = PropertyReader.methods[property_type](modded_file, property)

                if master_value != modded_value:
                    key = f"[Object={object_name}][Potential Properties][Property={property['Property']}]"
                    mod[Mod.MODDED_FILES][modded_file_relative_path.as_posix()][key] = {
                        Mod.OFFSET: key,
                        Mod.ORIGINAL_VALUE: master_value,
                        Mod.MODDED_VALUE: modded_value,
                    }
                    show_message(f"    Extracted -> {key}")
                    # print(f"master_value: {master_value}")
                    # print(f"modded_value: {modded_value}")
                    # print('')

        master_file.close()
        modded_file.close()

    # Write mod to definition file
    write_mod_details_to_file(mod, mod[Mod.DEFINITION_FILE_PATH])
    show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)
    return True
