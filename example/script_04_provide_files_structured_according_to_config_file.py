#!/usr/bin/env python
# coding: utf-8

# script_provide_files_structured_according_to_config_file
# version 1p4

# go to folder with integration results
# find files to work with
# create forder descriptor in folder_root_work
# read selected files
# save selected files as npys to this folder
###


import os
import numpy as np

DEBUG = False

from shared_functions import func_sorted_alphanum, func_create_config_object, func_return_projects_to_refine, func_descriptor_from_projct_name


class ClassSearch():
    """
    What should we do?
    Is there an option to create variables from the json? There is but how to implement it in the way that makes us live most easy?
    It would be great if we could convert the json dict to a dataclass that lives inside the class we're in at the moment -> then we do not initialize soo much...
    nevertheless, it will need some work if we want to make a very universal procedure
    """

    def __init__(self, mask=None):
        self.all_files = []
        self.scan_first = None
        self.scan_last = None
        self.dir_to_search = None

    def get_all_files(self, dir_to_search, filetypes=['dat']):
        """
        """
        all_files = func_sorted_alphanum([os.path.join(dirpath, filename) for dirpath, _, filenames in os.walk(
            dir_to_search) for filename in filenames for ending in filetypes if filename.endswith(ending)])
        self.all_files = all_files

    def provide_files_of_interest(self):
        """
        """
        def loc_func_get_characteristic(string):
            """
            check if file segment is integer
            """
            #string = os.path.basename(os.path.dirname(string)).split('_')[-2]
            string = os.path.basename(string)
            string = os.path.splitext(string)[0]
            string = string.split('_')[-1]

            def is_integer(n):
                """
                """
                try:
                    int(n)
                    # print(n, end=' ')
                    return int(n)
                except ValueError:
                    return False
                #else:
                #    print(string, end=' ')
                #    return int(n)
            return is_integer(string)
        
        def loc_func_number_in_filename(file, range_beg, range_end):
            number = loc_func_get_characteristic(file)
            if range_beg <= number <= range_end:
                print(number, end=' ')
                return True

        range_beg, range_end = self.scan_first, self.scan_last
        if range_beg >= range_end:
            print(f'WARNING: {range_beg} >= {range_end}')
        print('range_beg, range_end:   ', range_beg, range_end)
        files_of_interest = [file for file in self.all_files if loc_func_number_in_filename(file, range_beg,  range_end)]
        self.files_of_interest = files_of_interest


DATA_FOR_ANALYSIS = 'data_for_analysis'

projects_to_refine = func_return_projects_to_refine('projects_to_refine.json')

for project in projects_to_refine:
    
    print('\n\n')
    descriptor = func_descriptor_from_projct_name(project)
    config_file = f'{descriptor}.json'
    config_file = os.path.join(project, config_file)
    print(config_file)

    config = func_create_config_object(config_file)

    search = ClassSearch()
    search.scan_first = config.scan_first
    search.scan_last = config.scan_last
    dir_to_search = os.path.expanduser(config.folder_root_integrated)
    dir_to_search = os.path.join(dir_to_search, "")
    search.get_all_files(dir_to_search=dir_to_search)
    search.provide_files_of_interest()

    # print(search.all_files)

    print(search.files_of_interest)

    for file in search.files_of_interest:
        if '-5.5' in file:
                # my file scheme is: tth, i, q
                # want to save q, i only
                #strip_that = len(dir_to_search)
                #base_name = file[strip_that:]
            base_name = os.path.basename(file)
            base_name = os.path.splitext(base_name)[0]
            base_name = f"{base_name}.npy"
            #path_out = os.path.join(                    config.folder_work_root, config.descriptor)
            path_out = os.path.join(project, DATA_FOR_ANALYSIS)
            file_name = os.path.join(path_out, base_name)
            # print(file_name)
            if not os.path.exists(file_name):
                os.makedirs(path_out, exist_ok=True)
                print(f'looking at file \n {file}')
                tth, i, *_ = np.genfromtxt(file).T  # [1:]
                energy = 18.0 - 0.007
                q = 4.0 * np.pi / (12.3985 / energy) * \
                    np.sin(np.deg2rad(0.5 * tth))
                # print(i)
                arr_out = np.array([q, i])
                if arr_out.shape[0] != 2:
                    arr_out = arr_out.T
                if DEBUG:
                    import matplotlib.pyplot as plt
                    plt.plot(*arr_out)
                    plt.show()
                print(os.path.abspath(file_name))
                np.save(file_name, arr_out)
