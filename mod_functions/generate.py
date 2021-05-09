import os.path
import re
import shutil
import subprocess
from pathlib import Path
from pprint import pprint
from typing import Dict
from zipfile import ZipFile

from pyrotools.console import cprint, COLORS

import config
import globals
import messages as m
from constants import GENERATED_MODS_OUTPUT_FOLDER, Mod, PLUGIN_FILE_KEYS, KEY_REGEX, SUPPORTED_PROPERTY_TYPES, \
    UNREAL_PACK_COMMAND, PLUGIN_FILE_EXTENSION, COMPILED_PAKS_FOLDER_LOCATION, PAK_FILE_SIZE_MINIMUM, ZIP_GENERATED_MODS
from hex import PropertyWriter
from utils import get_mod_name, check_valid_folder, trigger_error, get_corresponding_master_file, load_json_from_file, \
    get_json_index_filepath, write_mod_details_to_file, recursive_search, cmd_exists, show_message, stdout_to_output


def all():
    for mod in globals.mods.values():
        one(mod)


def one(mod: Dict):
    mod_name = get_mod_name(mod)
    show_message(f"{'=' * 10} {m.GENERATING_MOD.format(mod_name)} {'=' * 10}", COLORS.BRIGHT_CYAN, important=True)

    if Mod.MODDED_FILES not in mod or not mod[Mod.MODDED_FILES]:
        return trigger_error(m.E_MOD_NOT_DEFINED_YET.format(mod[Mod.DEFINITION_FILE_PATH]), halt=False)

    # Create destination folder architecture
    output_folder_path = Path(config.get_string(GENERATED_MODS_OUTPUT_FOLDER)) / mod_name
    paks_folder_path = output_folder_path / COMPILED_PAKS_FOLDER_LOCATION
    input_folder_path = Path(mod[Mod.INPUT_FOLDER])
    pak_config_file_path = input_folder_path.parent / 'unrealpak_config.txt'
    # pak_config_file_path = output_folder_path / f"{mod[Mod.DEFINITION_FILE_PATH].stem}.txt"

    shutil.rmtree(output_folder_path, ignore_errors=True)  # Clear Output folder
    output_folder_path.mkdir(parents=True, exist_ok=True)
    paks_folder_path.mkdir(parents=True, exist_ok=True)
    input_folder_path.mkdir(parents=True, exist_ok=True)  # Should already exist, but just in case
    shutil.rmtree(input_folder_path / "Content", ignore_errors=True)  # Clear Content folder in case old files in there

    for modded_file_relative_location, file_changes in mod[Mod.MODDED_FILES].items():
        # Get corresponding master file and absolute modded file path
        master_file_path = get_corresponding_master_file(mod, Path(modded_file_relative_location))
        modded_file_path = input_folder_path / modded_file_relative_location

        # copy file over
        modded_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(master_file_path, modded_file_path)

        # Generate json index file (If needed) and load it
        if not (json_index := load_json_from_file(get_json_index_filepath(master_file_path))):
            return False

        show_message(modded_file_path)

        modded_file = open(modded_file_path, "r+b")
        for key, changes in file_changes.items():
            matches = re.findall(pattern=KEY_REGEX, string=key, flags=re.IGNORECASE)
            property = recursive_search(json_index['ExportValues'], matches)
            # pprint(property)

            if 'Type' not in property:
                continue

            property_type = property['Type']
            # If this property type is not supported, pass it
            if property_type not in SUPPORTED_PROPERTY_TYPES:
                continue

            if PropertyWriter.methods[property_type](modded_file, property, changes[Mod.MODDED_VALUE]):
                show_message(f"    Wrote -> {key}")

        modded_file.close()

    # Pack/Compile Pak file
    if cmd_exists(unreal_pack_cmd := config.get_string(UNREAL_PACK_COMMAND)):
        with open(pak_config_file_path, 'w') as pak_config_file:
            pak_config_file.write(f"\"{input_folder_path}/\" \"../../../FSD/\"")

        pak_file_path = paks_folder_path / (mod_name + f" {mod[Mod.VERSION_NAME]}_P.pak")
        # pak_file_path = paks_folder_path / (mod_name + "_P.pak")
        plugin_file_name = f"{mod_name}.{PLUGIN_FILE_EXTENSION}"
        plugin_file_path = output_folder_path / plugin_file_name
        zip_archive_file_path = Path(config.get_string(GENERATED_MODS_OUTPUT_FOLDER)) / (mod_name + ".zip")

        # Write .upugin file, then definition file for new FileVersion (and master version if it was just updated)
        write_mod_details_to_file(mod, plugin_file_path, increment_file_version=True)
        write_mod_details_to_file(mod, mod[Mod.DEFINITION_FILE_PATH])

        proc = subprocess.Popen([
            unreal_pack_cmd,
            f"\"{pak_file_path}\"",
            f"-Create=\"{pak_config_file_path}\"",
            "-compress"
        ], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)
        proc.wait()

        if not pak_file_path.is_file():
            trigger_error(m.E_FAILED_CREATE_PAK, halt=False)
            print(stdout_to_output(proc.stdout))
            return
        elif os.path.getsize(pak_file_path) < PAK_FILE_SIZE_MINIMUM:
            trigger_error(m.E_PAK_FILE_WRONG_SIZE, halt=False)
            print(stdout_to_output(proc.stdout))
            return
        else:
            show_message(stdout_to_output(proc.stdout))

        pak_config_file_path.unlink(missing_ok=True)

        if config.get_boolean(ZIP_GENERATED_MODS, True):
            with ZipFile(zip_archive_file_path, 'w') as zipObj:
                zipObj.write(pak_file_path, pak_file_path.relative_to(output_folder_path.parent))
                zipObj.write(plugin_file_path, f"{mod_name}/{plugin_file_name}")

        show_message(f"{m.DONE}\n", COLORS.BRIGHT_CYAN, important=True)
    else:
        trigger_error(m.E_COMMAND_NOT_FOUND.format(unreal_pack_cmd, UNREAL_PACK_COMMAND), halt=False)
