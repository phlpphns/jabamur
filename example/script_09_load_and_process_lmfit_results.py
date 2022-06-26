#!/usr/bin/env python

# script_load_and_process_lmfit_results
# version 2p6

# TODO: only do new extraction on demand

import os
import numpy as np
import matplotlib.pyplot as plt
import glob

import pandas as pd

from scipy.interpolate import interp1d

#import pybaselines
# from pybaselines import utils


#from collections import namedtuple
#import json

from lmfit.model import load_modelresult
# from lmfit.models import GaussianModel, LorentzianModel, QuadraticModel, LinearModel, PseudoVoigtModel, ExponentialModel, PowerLawModel, PolynomialModel, ConstantModel, Model, VoigtModel


#import dill as pickle
#import pickle

from shared_functions import func_sorted_alphanum, func_create_config_object, func_descriptor_from_projct_name

from simple_parsing import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--do_extraction", default='no',
                    help="list of peak parameters to be extracted")
parser.add_argument("--extract_peaks", type=list, default=False,
                    help="list of peak parameters to be extracted")

args = parser.parse_args()


widthOfImage, heightOfImage = 10, 5.5


PROJECT_FOLDER = './projects_fitting/'
DIR_RESULTS_FITS = './00_extracted_results'


#config_files = [config_file for config_file in glob.glob(    f'{CONFIG_FILE_FOLDER}*.json')]
# print(config_files)

extract_these = ['GST_cub_111', 'Ge_111',
                 'GST_cub_200', 'GST_trig']

list_of_errors = []


#"""
import dill as pickle   # needed to pickle from parallel loop


def func_save_pickle(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def func_load_pickle(name):
    with open(name, 'rb') as f:
        return pickle.load(f)
#"""


def func_imdims(widthOfImage, heightOfImage, a, b):
    return widthOfImage * a, heightOfImage * b


def plot_and_size(dimens=func_imdims(widthOfImage, heightOfImage, 1, 1)):
    return plt.figure(figsize=(dimens))


from joblib import Parallel, delayed


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


def func_prep_optional_abscissa(array_with_one_maximum):
    """
    """
    alternative = array_with_one_maximum.copy()
    max_val = max(alternative)
    index = np.argmax(alternative)
    alternative[index:] *= -1
    alternative[index:] += 2 * max_val
    print(max_val, index)
    return alternative


def func_load_or_pickle_load(result):
    #result_pickled = result[:-len(ENDING_RESULT_FILE)]
    result_pickled = os.path.splitext(result)[0]
    result_pickled = os.path.basename(result_pickled)
    folder_pickle = os.path.join(DIR_RESULTS_FITS, 'pickle')
    os.makedirs(folder_pickle, exist_ok=True)

    result_pickled = os.path.join(folder_pickle, result_pickled)
    result_pickled = f'{result_pickled}.pkl'
    print(result_pickled)
    try:
        result = func_load_pickle(result_pickled)
        print("loaded existing pickled result")
    except:
        result = load_modelresult(result)
        func_save_pickle(result, result_pickled)
        print('result needed to be loaded from txt file. saved as pickle')
    return result


def func_fill_dict_collected(results, temperatures, epochs, dict_collected):
    for index, result in enumerate(results):  # loop over all result files
        print(result)
        try:
            #result = results[index] = func_load_or_pickle_load(result)
            result = func_load_or_pickle_load(result)
            keys = result.result.params.keys()
            for prefix in extract_these:
                try:
                    relevant = [key for key in keys if key.startswith(prefix)]
                    # print(relevant)
                    # only parameter values without prefix
                    strip_that = len(f'{prefix}_')
                    dict_rel = {key[strip_that:]: result.result.params.get(
                        key).value for key in relevant}
                    dict_rel['temperature'] = temperatures[index]
                    dict_rel['epoch'] = epochs[index]
                    #dict_rel['optional_abscissa'] = optional_abscissa[index]
                    dict_rel['size'] = 2 * np.pi / dict_rel['fwhm'] / 10.
                    dict_rel['d'] = 2 * np.pi / dict_rel['center']
                    # print(dict_rel)
                    dict_collected[prefix] = dict_collected[prefix].append(
                        dict_rel, ignore_index=True)
                    dict_rel = {}
                except Exception as e:
                    print(f'error in extraction:    {e}')
                    print(f'no entry with {prefix} does exist')
        except Exception as e:
            print(e)
            list_of_errors.append([e])


ENDING_RESULT_FILE = "fitres"


def func_extract(extract_these):
    """
    if temperature-log exists read it into the dataframe, else provide index numbers
    find all results
    load them as pickle
        or load them from text and save them às pickle 
    extract parameters
    """
    folders = next(os.walk(PROJECT_FOLDER))[1]
    folders = [os.path.join(PROJECT_FOLDER, folder) for folder in folders]
    ending = '.project'
    projects = [folder for folder in folders if folder.endswith(ending)]
    for project in projects:
        os.makedirs(DIR_RESULTS_FITS, exist_ok=True)

        dir_results_fits = os.path.join(project, "results", "")

        if not os.path.isdir(dir_results_fits):
            continue

        print(project, dir_results_fits)
        descriptor = func_descriptor_from_projct_name(project)

        json_file = f'{descriptor}.json'
        json_file = os.path.join(project, json_file)
        print(json_file)

        config = func_create_config_object(json_file)
        #dir_results_fits = os.path.join(            DIR_RESULTS_FITS, descriptor, "")
        results = [result for result in glob.glob(
            f'{dir_results_fits}*.{ENDING_RESULT_FILE}')]
        results = func_sorted_alphanum(results)

        print(results)
        epochs = [result.split('epoch')[-1] for result in results]
        print(epochs)
        epochs = [string.split('_')[0] for string in epochs]
        print(epochs)

        # print(results)

        dict_collected = {key: pd.DataFrame()
                          for key in extract_these}  # create empty pandas dataframe

        print(dict_collected)

        try:
            temperature_file = os.path.join(
                config.dir_temperature_log, config.temperature_log)
            print(temperature_file)
            _, times, temperatures = np.genfromtxt(temperature_file).T
            #plt.plot(times, temperatures)
            # plt.show()
            helperFunction = interp1d(times, temperatures)
            temperatures = helperFunction(epochs)
            print('temperatures loaded and interpolated')
        except:
            try:
                temperatures = np.genfromtxt(temperature_file).T[1]
            except:
                temperatures = np.arange(len(epochs))

        # print(ieiaeiaeiae)

        #optional_abscissa = func_prep_optional_abscissa(temperatures)

        print(temperatures)

        func_fill_dict_collected(results, temperatures, epochs, dict_collected)

        # print(dict_collected)
        for key in dict_collected.keys():
            data_frame = dict_collected[key]
            name_out = f'{DIR_RESULTS_FITS}/result_fits_{config.descriptor}_{key}.txt'
            print(name_out)
            data_frame.to_csv(name_out, index=False)
        # ============================================
        # Comparisons constant artefact


if args.do_extraction == 'yes':
    func_extract(extract_these)


data_frames = [data_frame for data_frame in glob.glob(
    f'{DIR_RESULTS_FITS}/*.txt')]
print("printing data_frames:   ", len(data_frames), data_frames)

dict_all_results = {f'k_{index}': frame for index,
                    frame in enumerate(data_frames)}
print(dict_all_results)

#from pylib_plot_datasets import func_compare_charas_n


for index, key in enumerate(dict_all_results.keys()):
    pattern = dict_all_results.get(key)
    #print('key:   ', key)
    #print('item:   ', pattern)
    file_name = os.path.join(pattern)
    #file_name = os.path.join(csv_path, f'{pattern}.txt')
    try:
        loaded_results = pd.read_csv(file_name)
    except:
        continue
    dict_all_results[key] = loaded_results

    print(pattern)

    keys = loaded_results.keys()

    for key in keys:
        fig_name = os.path.splitext(pattern)[0]
        fig_name = f'{fig_name}_{key}.png'
        if fig_name == pattern:
            print("CANNOT OVERWRITE FILE")
            continue
        plt.figure(figsize=(func_imdims(widthOfImage, heightOfImage, 1., 1.)))
        plt.title(key)
        plt.plot(loaded_results[key], label='data')
        plt.savefig(fig_name)
        # plt.clf()
        plt.close()
    #best = result.best_fit + bckg
    #plt.plot(xdat, best, label='best fit')

# print(dict_all_results)

for element in list_of_errors:
    print(element)


print('script extraction of results finished')
