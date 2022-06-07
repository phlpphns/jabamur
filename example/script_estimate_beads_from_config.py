#!/usr/bin/env python
# coding: utf-8

# version 1p5

# go to folder with integration results
# find files to work with
# create forder descriptor in folder_root_work
# read selected files
# save selected files as npys to this folder
###


# for all folders
# was will ich eigentlich machen? -> Ich will mir für jeden Ordner bckg
# erstellen lassen, falls noch nicht vorhanden.
# Anhand welchen Kriteriums bestimme Ich vorhanden und nicht vorhanden?
# d.h. welche config Datei wird ausgesucht? - Es ist alles ein scheiß, weil
# Ich irgendwo angeben müsste was nicht passt bzw welche Dateien ausgenommen
# werden sollen. -> Hier bräuchte man ein Tool um die Auswahl einfach und
# übersichtlich zu gestalten.
# maybe loop over all available -> if graph looks good then save a config
# file, otherwise jump over. If there is a config file available don't plot.
# Otherwise load the template.
###


import pybaselines
import matplotlib.pyplot as plt

import os
import glob
import numpy as np

import json

#import sys

from shared_functions import func_sorted_alphanum, func_return_projects_to_refine

from simple_parsing import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--spacing", type=int, default=15,
                    help="how many files should be skipped")
args = parser.parse_args()

SPACING = args.spacing


def func_plot_bl_from_para(dataset, freq_cutoff, lam_0, lam_1, lam_2, asymmetry, **kwargs):
    try:
        x, y = dataset
    except:
        x, y = dataset.T

    bckg_estimated = pybaselines.misc.beads(
        y, freq_cutoff, lam_0, lam_1, lam_2, asymmetry)[0]
    plt.plot(x, y)
    plt.plot(x, bckg_estimated, color='black')


COPY_FROM = "./projects_fitting/template_beads_parameters.beads_parameters"
DATA_FOR_ANALYSIS = 'data_for_analysis'



projects_to_refine = func_return_projects_to_refine('projects_to_refine.json')

for project in projects_to_refine:

        config_file = os.path.basename(project)
        descriptor = os.path.splitext(config_file)[0]
        beads_file = f'{descriptor}.beads_parameters'
        beads_file = os.path.join(project, beads_file)
        file_name = os.path.join(project, "list_of_files")

        folder_data_for_analysis = os.path.join(project, DATA_FOR_ANALYSIS, "")

        new_beads_parameters_file = os.path.join(
            project, f'{descriptor}.beads_parameters')

        if os.path.isfile(new_beads_parameters_file):
            print(f'{new_beads_parameters_file} already exists')
            continue
        else:
            template_beads_parameters_file = os.path.join(COPY_FROM)

            try:
                with open(template_beads_parameters_file) as json_file:
                    new_beads = json.load(json_file)
            except:
                new_template = {
                    "descriptor": "dummy_descriptor",
                    "beads_parameters": {
                        "freq_cutoff": 0.025,
                        "lam_0": 0.0435,
                        "lam_1": 0.15,
                        "lam_2": 0.2,
                        "asymmetry": 25.0
                    },
                    "beads_comment": ""
                }
                print(new_template)
                choice = input(
                    'no template file there. should a new one "{template_beads_parameters}" be saved? y/n  ')
                if choice in ['y', 'Y']:
                    with open(f'{template_beads_parameters_file}', 'w') as fp:
                        json.dump(new_template, fp, indent=4)
                    print(f'file {template_beads_parameters_file} saved')
                import sys
                print("script terminates now ")
                sys.exit()

            beads_parameters = new_beads.get('beads_parameters')

            # npys = [npy for npy in glob.glob(f'./*-5.5*.npy')]
            npys = [npy for npy in glob.glob(
                f'{folder_data_for_analysis}*.npy') if not npy.endswith('bckg.npy')]
            npys = func_sorted_alphanum(npys)[:]
            print(npys)

            npys = npys[::SPACING]

            work = [np.load(npy).T for npy in npys]

            for index, dataset in enumerate(work):
                try:
                    func_plot_bl_from_para(dataset, **beads_parameters)
                except:
                    print('error at   ', index, ' / ', len(work))
            plt.title(descriptor)
            plt.savefig(f'{project}/baselines_{descriptor}.png')
            plt.show()
            # plt.close()

            choice = input(
                f'should the current beads parameters be saved to the file "{new_beads_parameters_file}" ? y/n   ')

            if choice in ['y', 'Y']:
                new_beads['descriptor'] = descriptor

                with open(new_beads_parameters_file, 'w') as fp:
                    json.dump(new_beads, fp, indent=4)  # , sort_keys=True)

                print(f'{new_beads_parameters_file} was created')
            else:
                print('not saved')

print('script finished')
