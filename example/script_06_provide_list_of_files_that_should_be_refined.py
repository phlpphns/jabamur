#!/usr/bin/env python
# coding: utf-8

# script_provide_list_of_files_that_should_be_refined
# version 1p3

# go to folder with integration results
# find files to work with
# create forder descriptor in folder_root_work
# read selected files
# save selected files as npys to this folder
###


#import json
#import csv
import os
import glob
import numpy as np
import pandas as pd

from shared_functions import func_create_config_object, func_return_projects_to_refine, func_sorted_alphanum, func_descriptor_from_projct_name


from simple_parsing import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--first", type=int, default=None,
                    help="first index of list of files")
parser.add_argument("--last", type=int, default=None,
                    help="last index of list of files")
parser.add_argument("--spacing", type=int, default=None,
                    help="how many files should be skipped")


#CONFIG_FILE_FOLDER = './config_files/'
FIT_RESULTS_FOLDER = './results/'

#config_files = [config_file for config_file in glob.glob(    f'{CONFIG_FILE_FOLDER}*.json')][0:]


args = parser.parse_args()
print("first:", args.first)
print("last:", args.last)
print("spacing:", args.spacing)

start_at = args.first
end_at = args.last
spacing = args.spacing

projects_to_refine = func_return_projects_to_refine('projects_to_refine.json')

for project in projects_to_refine:
    print(project)
    outfile_name = f"{project}/list_of_files"
    descriptor = func_descriptor_from_projct_name(project)
    config_file = f'{descriptor}.json'
    config_file = os.path.join(project, config_file)
    print(config_file)
    print(outfile_name)
    config = func_create_config_object(config_file)
    fit_results_folder = os.path.join(
        project, "results")

    ending = ".npy"

    data_dir = os.path.join(project, "data_for_analysis", "")
    all_paths = [npy for npy in glob.glob(f'{data_dir}*{ending}')]
    all_paths = filter(lambda x: not x.endswith('bckg.npy'), all_paths)
    all_paths = list(all_paths)
    all_paths = func_sorted_alphanum(all_paths)
    all_paths = all_paths[start_at:end_at:spacing]

    all_files = [os.path.basename(file) for file in all_paths]
    all_results = [os.path.basename(file) for file in all_paths]
    all_results = [file[:-len(ending)] for file in all_results]
    all_results = [os.path.join(fit_results_folder, file)
                   for file in all_results]

    df = pd.DataFrame(np.array([all_paths, all_results]).T, columns=[
                      'datafile', 'results'])
    # print(df)
    df.to_csv(outfile_name, index=False, sep='\t')
    print(f'----- {outfile_name} written')
