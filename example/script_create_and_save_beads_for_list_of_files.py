#!/usr/bin/env python
# coding: utf-8

# version 1p3

import pybaselines
#import matplotlib.pyplot as plt

import os
import glob
import numpy as np
import pandas as pd

from shared_functions import func_create_config_object, func_return_projects_to_refine

from simple_parsing import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--overwrite", default=False,
                    help="overwrite existing baseline file yes/no")

args = parser.parse_args()

OVERWRITE = False
if args.overwrite == 'yes':
    OVERWRITE = True


projects_to_refine = func_return_projects_to_refine('projects_to_refine.json')

for project in projects_to_refine:

    config_file = os.path.basename(project)
    config_file = os.path.splitext(config_file)[0]
    beads_file = f'{config_file}.beads_parameters'
    beads_file = os.path.join(project, beads_file)
    file_name = os.path.join(project, "list_of_files")

    try:
        print(beads_file)
        beads_config = func_create_config_object(beads_file)
    except:
        print(f'{beads_file} could not be found')
        continue

    try:
        list_of_files = pd.read_csv(file_name, sep='\t')
    except:
        print(f'{file_name} could not be found')
        continue

    # read column datafile
    files_to_process = list_of_files['datafile']

    beads_parameters = beads_config.beads_parameters
    for path_to_file in files_to_process:
        out_name = os.path.splitext(path_to_file)[0]
        out_name = f'{out_name}.bckg.npy'

        if os.path.isfile(out_name) and not OVERWRITE:
            print(f'{path_to_file} already exists')
            continue
        x, y = np.load(path_to_file)
        bckg_estimated = pybaselines.misc.beads(
            y, **beads_parameters)[0]

        np.save(out_name, bckg_estimated)
        print(f'{path_to_file} written')

    # else:
    #    print(f'no beads file {beads_file}')


print('script beads finished')
