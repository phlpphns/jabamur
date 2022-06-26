
#!/usr/bin/env python

import glob
import os
import json
import shutil

#CONFIG_FILE_FOLDER = './config_files/'
CONFIG_FILE_FOLDER = './'
### TODO: hard code template_refine.refine
COPY_FROM = "../template_refine.refine"

config_files = [config_file for config_file in glob.glob(
    f'{CONFIG_FILE_FOLDER}*.json')]

print(config_files)

for config_file in config_files:

    with open(config_file) as json_file:
        config = json.load(json_file)

    descriptor = config.get('descriptor')
    name_folder = f'{descriptor}.project'
    os.makedirs(name_folder, exist_ok=True)
    file_to_move = config_file
    try:
        shutil.move(file_to_move, name_folder)
    except Exception as e:
        print(e)
    try:
        file_to_move = f'{descriptor}.beads_parameters'
        shutil.move(file_to_move, name_folder)
    except:
        print(f'{file_to_move} does not exist')

    new_refine_file = os.path.join(
        CONFIG_FILE_FOLDER, f'./{name_folder}/{descriptor}.refine')
    if os.path.isfile(new_refine_file):
        print(f'{new_refine_file} already exists')
        continue
    else:
        template_refine_parameters_file = os.path.join(
            CONFIG_FILE_FOLDER, COPY_FROM)

        with open(template_refine_parameters_file) as json_file:
            new_refine = json.load(json_file)

        new_refine['descriptor'] = descriptor

        with open(new_refine_file, 'w') as fp:
            json.dump(new_refine, fp, indent=4)  # , sort_keys=True)

        print(f'{new_refine_file} was created')
