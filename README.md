# Deep Rock Galactic Mod Validator

### Introduction
Got tired of needing to manually check if my mods were still working between hotfixes/updates, or if they were still working but not including the latest changes.
This utility will save you some time making those verifications for you, so you can set it up then quickly run it after a new hotfix/update is deployed.

This utility has 2 different functions, described below. **Before using this utility, you must edit the `settings.ini` file!!**

### Usage 1 - Mod Validator
Used to check if, it will:
1. Recursively scan all the `uexp` files you use in your mods folders
2. Find the corresponding files in the extracted vanilla folder
3. Compare and tell you if the file sizes differ, indicating it needs updating.

Settings needed:
- `MODDED_CONTENT_FOLDER_PATHS` = list of folders where your mods are
- `LATEST_CONTENT_FOLDER_PATH` = path to extracted vanilla files

### Usage 2 - Hotfix/Update Changes Detector
Will
1. recursively scan all the `uexp` files you use in your mods 
2. Find the corresponding

Settings needed:
- `MODDED_CONTENT_FOLDER_PATHS` = list of folders where your mods are
- `LATEST_CONTENT_FOLDER_PATH` = path to extracted vanilla files
- `PREVIOUS_CONTENT_FOLDER_PATH` = path to extracted vanilla files (previous verison)
