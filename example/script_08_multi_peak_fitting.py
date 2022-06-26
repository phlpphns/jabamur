#!/usr/bin/env python

# script_multi_peak_fitting
# version 2p8

# preprocess all files up to the point where all is in the folder "data_for_analysis"
# in that folder should be the data and background for the fits

import os
import numpy as np
import glob
import pandas as pd

from lmfit.model import save_modelresult, load_modelresult

from shared_functions import func_sorted_alphanum, func_create_config_object, gene_load_list_of_files, func_plot_result, func_lmfit, func_descriptor_from_projct_name, func_return_projects_to_refine


from simple_parsing import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--debug", default=False,
                    help="plot images of data to check the process")
parser.add_argument("--parallel", default=False,
                    help="True or False for parallel processing")
parser.add_argument("--number_of_processes", type=int,
                    default=8, help="integer for how many processes should run in parallel")

args = parser.parse_args()

DEBUG = False
if args.debug == 'yes':
    DEBUG = True

PARALLEL = False
if args.parallel == 'yes':
    from joblib import Parallel, delayed
    PARALLEL = True
    NUMBER_OF_PROCESSES_FOR_PARALLEL_LOOP = args.number_of_processes
    print("parallel argument activated")

#CONFIG_FILE_FOLDER = './config_files/'
#FIT_RESULTS_FOLDER = './results/'


widthOfImage, heightOfImage = 10, 5.5

spacer_error = '---------------------'


def func_prepare_process(config_file, DIR_PNGS, DIR_RESULTS_FITS):
    print('======================================================================')
    print('======================================================================')
    print('======================================================================')
    print(f'CONFIG FILE IS:   {config_file}')
    config = func_create_config_object(config_file)
    print()
    print(f"WORKING ON DATASET:  {config.descriptor}")

    dir_pngs = os.path.join(DIR_PNGS, config.descriptor, "")
    if not os.path.isdir(dir_pngs):
        os.makedirs(dir_pngs)

    dir_results_fits = os.path.join(DIR_RESULTS_FITS, config.descriptor, "")
    if not os.path.isdir(dir_results_fits):
        os.makedirs(dir_results_fits)
    return (config, dir_pngs, dir_results_fits)


def func_pipeline(file_name, dataset, config, path_result):
    out_name = f"{path_result}.fitres"
    if not os.path.isfile(out_name) or config.overwrite:
        print(f"WORKING ON: \n {file_name}")
        x, y, bckg = dataset
        if DEBUG:
            print(len(x), len(y))
            import matplotlib.pyplot as plt
            plt.plot(x, y)
            plt.plot(x, bckg)
            plt.show()

        out_name_fit_set = f"{path_result}.x_y_bckg"
        out_arr = np.array([x, y, bckg])
        out_dir = os.path.dirname(out_name_fit_set)
        os.makedirs(out_dir, exist_ok=True)

        result_fit = func_lmfit(x, y - bckg, config)

        print(f'{file_name} --- fit finished')

        try:
            save_modelresult(result_fit, out_name)
            np.save(out_name_fit_set, out_arr)
            print(f'{file_name} --- result written')
        except Exception as e:
            print("ERROR IN SAVING RESULT OR DATA")
            print(e)

        # func_save_pickle(result, out_name)
        try:
            func_plot_result(path_result, result_fit, x, y, bckg,
                             widthOfImage, heightOfImage)
        except Exception as e:
            print(f'\n\n\n ERROR IN FIT:    {e}')
            print(f'problem at \n {file_name} \n for set {out_name} \n\n\n')

        print(f'{file_name} --- leaving func_pipeline')


def func_refinementloop(PARALLEL):
    if PARALLEL:
        print('\n\n\n')
        try:
            print("start parallel loop")
            Parallel(n_jobs=NUMBER_OF_PROCESSES_FOR_PARALLEL_LOOP)(delayed(func_pipeline)(file_name, dataset, config,
                                                                                          path_result) for index, (file_name, dataset, path_result) in enumerate(gene_loaded_datasets))
            print("end parallel loop")
        except Exception as e:
            print()
            print(
                f"ERROR IN PARALLEL LOOP\n"
                f"{spacer_error}  ERROR WITH ATTEMPTING REFINEMENT AT    {refine_file}")
            print(spacer_error, spacer_error, e)
    else:
        # for index, dataset in enumerate(gene_loaded_datasets):
        #    func_pipeline(index, dataset, config, dir_results_fits, dir_pngs)

        try:
            for index, (file_name, dataset, path_result) in enumerate(gene_loaded_datasets):
                func_pipeline(file_name, dataset, config, path_result)
        except Exception as e:
            print()
            # should move this reference to refine_file
            print(
                f"{spacer_error}  ERROR WITH ATTEMPTING REFINEMENT AT    {refine_file}")
            print(spacer_error, spacer_error, e)


def func_sanity_check(dir_results_fits):
    """
    needs improvement because the out dir is not specified well enough now
    """
    print("start loading results as sanity check")
    results = [result for result in glob.glob(
        f'{os.path.join(dir_results_fits, "")}*.fitres')]
    results = func_sorted_alphanum(results)

    for index, result in enumerate(results):
        # print(result)
        try:
            #_ = func_load_pickle(result)
            _ = load_modelresult(result)
            # print("successful loading of file ---- {result} ---- ")
        except:
            print(f'error: could not load file ---- {result} ----')
    print("loading results finished")
    print(f"{len(results)} results should have been loaded")
    print()
    print()


print('LOADED files_to_refine:')


#DIR_LIST_OF_FILES = "./list_of_files"
#DIR_PNGS = "./results"
#DIR_RESULTS_FITS = "./results"


projects_to_refine = func_return_projects_to_refine('projects_to_refine.json')

for project in projects_to_refine:
    descriptor = func_descriptor_from_projct_name(project)
    refine_file = f'{descriptor}.refine'
    refine_file = os.path.join(project, refine_file)
    file_name = os.path.join(project, "list_of_files")

    #config, dir_pngs, dir_results_fits = func_prepare_process(            refine_file, DIR_PNGS, DIR_RESULTS_FITS)
    config = func_create_config_object(refine_file)
    #file_name = f"{DIR_LIST_OF_FILES}/{config.descriptor}.list_of_files"

    print(f'current project is:   {project}')

    try:
        list_of_files = pd.read_csv(file_name, sep='\t')
        files_to_process = list_of_files['datafile']
        results_to_save = list_of_files['results']

        # with open(file_name, 'r') as file:
        #    file_read = file.readlines()

        #files_to_process = [line.rstrip('\n') for line in file_read]
        #files_to_process = func_sorted_alphanum(files_to_process)
        gene_loaded_datasets = gene_load_list_of_files(
            files_to_process, results_to_save, config)
        print()
        print("list of files to be refined loaded and generator created")
        print()
        print(files_to_process)
    except Exception as e:
        print()
        print(f'{spacer_error} NO FILES TO LOAD PROVIDED AT {refine_file}')
        print(spacer_error, spacer_error, e)

        gene_loaded_datasets = None

        # possible TODO: could check if file exists and if it is empty all files are newly refined

        """
            if config.overwrite is True:
                try:
                    print(
                        f'{spacer_error} ATTEMPTING TO READ ALL NPY FILES IN WORKING DIRECTORY')
                    files_to_process = [
                        file_name for file_name in glob.glob(f'{config.npy_dir}*.npy')]
                    files_to_process = func_sorted_alphanum(files_to_process)

                    gene_loaded_datasets = gene_load_list_of_files(
                        files_to_process, config)
                except Exception as e:
                    print(e)
                    print('NOTHING TO READ, SETTING gene_loaded_datasets TO None')
                    gene_loaded_datasets = None

                print()
                print("list of files to be refined loaded and generator created")
                print()
                print(files_to_process)
            """

    func_refinementloop(PARALLEL)

    try:
        dir_results_fits = os.path.join(project, "results", "")
        # func_sanity_check(dir_results_fits)
    except:
        print('some error with checking the results')

print('script fitting finished')
