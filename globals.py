from pathlib import Path


# Temporary folder to manipulate modded files
from typing import Dict

temp_folder = Path("temp/")

master_content_folders: [str, Path] = {}
master_files: Dict[str, Dict[str, Path]] = dict()
mods: Dict[Path, Dict] = {}
unique_modded_files = {}
modded_files = []

original_json = {}
json_index = {}

latest_master_version = ''
previous_master_version = ''

verbose_output = None
