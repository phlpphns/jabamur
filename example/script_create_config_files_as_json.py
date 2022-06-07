#!/usr/bin/env python
# coding: utf-8

# script_create_config_files_as_json
# version 0p5


### This script creates config-files in the json format from a file of definitions
### it is adapted for the preparations of data from the beamtime at
### soleil in july 2021. Surely can be improved or generalized

# maybe implement a condition that hinders overwriting of existing json file

FOLDER_JSONS = './projects_fitting_/'
#DEFINITIONS_FILE = './documentation_of_beamtime/definitions_2021_soleil_july_proposal.def'
DEFINITIONS_FILE = './documentation_of_beamtime/definitions_2021_soleil_july_LP3.def'

import json
import csv
import os
import glob


def func_save_json(dict_config_file, out_folder='config_files', descr=None, ending='.json'):
    out_file = os.path.join(out_folder, f'{descr}{ending}')
    with open(out_file, 'w') as fp:
        json.dump(dict_config_file, fp, indent=4)  # , sort_keys=True)


def func_definitions_to_config_file(definitions_file, out_folder, energy):
    '''
    '''

    def func_translate_line(csv_line):
        """
        csv_line must be a list. It will be unpacked here
        """
        sample, descriptor, type_of_measurement, temperature_program, scans_per_pattern, aquisition_time_in_s, scan_first, scan_last = csv_line
        return sample, descriptor, type_of_measurement, temperature_program, int(scans_per_pattern), float(aquisition_time_in_s), int(scan_first), int(scan_last)

    with open(definitions_file, newline='') as csvfile:
        read = csv.reader(csvfile, delimiter='\t')
        lines_to_process = []
        for csv_line in read:
            if len(csv_line) < 8 or csv_line[0].startswith('#'):
                continue
            # print(csv_line)
            lines_to_process.append(csv_line)

        #b = [row for row in a]

        # print(lines_to_process)

    for index, row in enumerate(lines_to_process):
        print(f'HERE!!! {index}')

        if len(row) < 8:
            print(f'line {index} needs more entries')
            continue

        #m_to_A = 1e10

        #exp_type = 1.

        sample, descriptor, type_of_measurement, temperature_program, scans_per_pattern, aquisition_time_in_s, scan_first, scan_last = func_translate_line(
            row)

        dict_config_file = {}

        dict_config_file['energy'] = energy
        dict_config_file['sample'] = sample
        dict_config_file['descriptor'] = descriptor
        dict_config_file['type_of_measurement'] = type_of_measurement
        dict_config_file['temperature_program'] = temperature_program
        # "~/central_directory/link_to__measurement_journey_soleil_2021_july_integrated/"
        dict_config_file['folder_root_integrated'] = "./integrated"
        dict_config_file['aquisition_time_in_s'] = aquisition_time_in_s
        dict_config_file['segments_per_pattern'] = scans_per_pattern
        dict_config_file['scan_first'] = scan_first
        dict_config_file['scan_last'] = scan_last
        dict_config_file['copy_segments'] = [1]
        dict_config_file['folder_work_root'] = "./data_for_analysis"
        dict_config_file['dir_temperature_log'] = "./temperature_logs"
        dict_config_file['temperature_log'] = f"log_{scan_first}.log"

        func_save_json(
            dict_config_file, descr=dict_config_file['descriptor'], out_folder=out_folder)




os.makedirs(FOLDER_JSONS, exist_ok=True)


dict_config_file = func_definitions_to_config_file(
    DEFINITIONS_FILE, out_folder=FOLDER_JSONS, energy=18. - 0.07)


# # check what's there

# In[20]:


config_files = sorted([f for f in glob.glob(f"{FOLDER_JSONS}*.json")])
dict_jsons = {}
for file in config_files:
    print(file)
    with open(file, 'r') as f:
        dict_jsons[os.path.basename(file)] = json.load(f)

dict_jsons.keys()

print('script ended')
