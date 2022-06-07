#!/usr/bin/env python
# coding: utf-8

# script_create_config_files_as_json
# version 0p5


### This script creates a file with a list of all projects that should
### be refined
### could be completed by command line arguments


import json
import os
import re


def func_sorted_alphanum(listOfStrings):
    """ Sorts the given iterable in the way that is expected. Converts each given list to a list of strings

    Required arguments:
    listOfStrings -- The iterable to be sorted.

    """

    listOfStrings = [str(i) for i in listOfStrings]

    def convert(text): return int(text) if text.isdigit() else text
    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    return sorted(listOfStrings, key=alphanum_key)


def func_save_json(dict_config_file, out_folder='config_files', descr=None, ending='.json'):
    out_file = os.path.join(out_folder, f'{descr}{ending}')
    with open(out_file, 'w') as fp:
        json.dump(dict_config_file, fp, indent=4)  # , sort_keys=True)


FOLDER_SEARCH = 'projects_fitting'
FOLDER_ENDING = '.project'

folders = next(os.walk(FOLDER_SEARCH))[1]
folders = func_sorted_alphanum(folders)

dict_file_names = {}

dict_file_names['_general_comment'] = "refinement will be started only if value is set to 'refine' "
dict_file_names['projects_to_refine'] = []
dict_file_names['not_refined'] = []
print(folders)
for folder in folders:
    if folder.endswith(FOLDER_ENDING):
        key = os.path.join(FOLDER_SEARCH, folder)
        dict_file_names['projects_to_refine'].append(key)

print(dict_file_names)

func_save_json(dict_file_names, out_folder='.',
               descr='projects_to_refine', ending='.json')

print('script ended')
