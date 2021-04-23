import re
import shutil
from pathlib import Path
from pprint import pprint
from typing import Dict

from pyrotools.console import cprint, COLORS

import config
import globals
import messages as m
from constants import GENERATED_MODS_OUTPUT_FOLDER, Mod, PLUGIN_FILE_KEYS, KEY_REGEX, SUPPORTED_PROPERTY_TYPES
from property_reader import PropertyWriter
from utils import get_mod_name, check_valid_folder, trigger_error, get_corresponding_master_file, load_json_from_file, \
    get_file_json_counterpart, write_mod_properties_to_file, recursive_search


def all():
    for mod in globals.mods.values():
        one(mod)


# TODO FileVersion is increased in define() but maybe it should be in generate?
def one(mod: Dict):
    cprint(COLORS.BRIGHT_CYAN, "=" * 10, m.GENERATING_MOD.format(get_mod_name(mod)), "=" * 10)
    # check_valid_folder(config.get_string(GENERATED_MODS_OUTPUT_FOLDER))

    if Mod.MODDED_FILES not in mod or not mod[Mod.MODDED_FILES]:
        return trigger_error(m.E_MOD_NOT_DEFINED_YET.format(mod[Mod.DEFINITION_FILE_PATH]), halt=False)

    # Create destination folder architecture
    output_folder_path = Path(config.get_string(GENERATED_MODS_OUTPUT_FOLDER)) / mod[Mod.DEFINITION_FILE_PATH].stem
    input_folder_path = output_folder_path / 'input'
    output_folder_path.mkdir(parents=True, exist_ok=True)
    (output_folder_path / 'Content/Paks').mkdir(parents=True, exist_ok=True)
    input_folder_path.mkdir(parents=True, exist_ok=True)

    for modded_file_relative_location, file_changes in mod[Mod.MODDED_FILES].items():
        # Get corresponding master file and absolute modded file path
        master_file_path = get_corresponding_master_file(mod, Path(modded_file_relative_location))
        modded_file_path = input_folder_path / modded_file_relative_location

        #copy file over
        modded_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(master_file_path, modded_file_path)

        # Generate json index file (If needed) and load it
        json_index = load_json_from_file(get_file_json_counterpart(master_file_path))

        # Get relative path relative to the content root folder
        # modded_file_relative_path = modded_file_path.relative_to(content_root_path)

        # Copy from master file in correct folder, then edit that one with the modded data
        # modded_file = open(modded_file, "rb")
        # modded_file.close()

        for key, changes in file_changes.items():
            # Extract different keys from variable "key"

            # matches = re.search(pattern=KEY_REGEX, string=key, flags=re.IGNORECASE)
            # if not matches:
            #     trigger_error(f"Unable to parse {key}")
            # for x in range(1, )
            # globals.master_content_folders[matches.group(1)] = master_folder_path
            # print(f"Version {matches.group(1)} - {master_content_folder}")

            print(key)

            # pattern = re.compile(pattern=KEY_REGEX, string=key, flags=re.IGNORECASE)
            matches = re.findall(pattern=KEY_REGEX, string=key, flags=re.IGNORECASE)
            property = recursive_search(json_index['ExportValues'], matches)
            # pprint(property)

            if 'Type' not in property:
                continue

            property_type = property['Type']
            # If this property type is not supported, pass it
            if property_type not in SUPPORTED_PROPERTY_TYPES:
                continue

            modded_file = open(modded_file_path, "r+b")

            master_value = PropertyWriter.methods[property_type](modded_file, property, changes[Mod.MODDED_VALUE])
            modded_file.close()

            # print(changes[Mod.ORIGINAL_VALUE])
            # print(changes[Mod.MODDED_VALUE])

            # for (matches) in re.findall(pattern=KEY_REGEX, string=key, flags=re.IGNORECASE):
            #     print(matches)

                # yo = recursive(bob, ["Object=DFC_Haz_05_Lethal", "Potential Properties", "Property=ShortDifficultyName"])

            # pyjq.first(query, json_index)

        # Write .upugin file at the end, if everything is ok
        write_mod_properties_to_file(mod, output_folder_path / 'manifest.uplugin', PLUGIN_FILE_KEYS)


    cprint(COLORS.BRIGHT_CYAN, m.DONE, "\n")


