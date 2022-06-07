# version 2p6


import re
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import lmfit


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


from collections import namedtuple
import json


def func_read_json(file):
    with open(file) as json_file:
        json_file = json.load(json_file)
    return json_file


def func_return_projects_to_refine(json_file):
    """
    """
    projects = func_read_json(json_file)
    projects_to_refine = projects.get('projects_to_refine')
    return projects_to_refine


def func_create_config_object(config_file):
    """
    """
    # with open(config_file) as json_file:
    config = func_read_json(config_file)

    """
    try:
        #config = config._replace(maindir=os.path.join(            os.path.expanduser(config.maindir), ''))
        #config = config._replace(npy_dir=os.path.join(os.path.expanduser(        config.folder_root_work), config.descriptor, config.npy_dir, ""))
        config['npy_dir'] = os.path.join(os.path.expanduser(
            config.get('folder_work_root')), config.get('descriptor'), "")
        print(f"{config_file} completely loaded")
    except Exception as e:
        print('no npy_dir created')
        print(f"     ERROR IS: {e}")
    """

    config = namedtuple("config", config.keys())(*config.values())

    return config


def func_descriptor_from_projct_name(path):
    """
    """
    descriptor = os.path.basename(path)
    descriptor = os.path.splitext(descriptor)[0]
    return descriptor


def ___func_load_data(config):
    npy_path = os.path.expanduser(config.npy_dir)
    npys = [file_name for file_name in glob.glob(f'{npy_path}*.npy')]
    npys = func_sorted_alphanum(npys)[:]
    print("load files from: ", npy_path)
    # print(npy_path)
    #loaded = []
    for npy in npys:
        file_name = os.path.join(npy_path, npy)
        x, y = np.load(file_name).T

        lower, upper = config.range_of_interest

        lower = np.searchsorted(x, lower, 'right')
        upper = np.searchsorted(x, upper, 'left')

        cut_at = upper
        cut_from = lower
        x = x[cut_from:cut_at]
        y = y[cut_from:cut_at]
        xy = np.array([x, y])
        # loaded.append(xy)
        yield xy


def gene_load_list_of_files(files_to_process, results_to_save, config):
    """
    loads file and provides a trimmed [x, y] dataset
    """
    for index, _ in enumerate(files_to_process):
        file_name = files_to_process[index]
        path_result = results_to_save[index]

        # try to handle error like "too many values to unpack (expected 2)"
        try:
            x, y = np.load(file_name)
        except:
            x, y = np.load(file_name).T

        try:
            bckg = f'{os.path.splitext(file_name)[0]}.bckg.npy'
            bckg = np.load(bckg)
        except:
            bckg = np.zeros(len(x))

        lower, upper = config.range_of_interest

        lower = np.searchsorted(x, lower, 'right')
        upper = np.searchsorted(x, upper, 'left')

        cut_at = upper
        cut_from = lower
        x = x[cut_from:cut_at]
        y = y[cut_from:cut_at]
        bckg = bckg[cut_from:cut_at]
        xyb = np.array([x, y, bckg])
        yield (file_name, xyb, path_result)
        # loaded.append(xy)
        # return loaded
        #?yield


def func_imdims(widthOfImage, heightOfImage, a, b):
    return widthOfImage * a, heightOfImage * b


# def plot_and_size(dimens=func_imdims(widthOfImage, heightOfImage, 1, 1)):
#    return plt.figure(figsize=(dimens))


def func_plot_result(path_result, result, xdat, ydat, bckg, widthOfImage, heightOfImage):
    params = result.params

    comps = result.eval_components()

    # print(result.fit_report(min_correl=0.5))

    plt.figure(figsize=(func_imdims(widthOfImage, heightOfImage, 1., 1.)))
    plt.plot(xdat, ydat, label='data')
    best = result.best_fit + bckg
    plt.plot(xdat, best, label='best fit')

    bckg_fit = bckg[:]
    for name, comp in comps.items():
        if name.startswith('bckg_'):
            bckg_fit += comp

    plt.plot(xdat, ydat - best + min(bckg_fit), label='diff')
    plt.plot(xdat, bckg_fit, label='bckg')
    # print(params)
    for name, comp in comps.items():
        if not name.startswith('bckg_'):
            line, = plt.plot(xdat, comp + bckg_fit, '--', label=name)
            pos = params[f'{name}center'].value
            ymin, ymax = plt.ylim()
            xytext = (0, 15)
            arrowprops = {'width': 1, 'headwidth': 1,
                          'headlength': 1, 'shrink': 0.05}
            plt.axvline(pos, color=line.get_color())
            plt.annotate(name, xy=(pos, ymax), xytext=xytext, textcoords='offset points',
                         rotation=0, va='bottom', ha='center', annotation_clip=False, arrowprops=arrowprops)
    plt.legend(loc='upper right')
    # plt.savefig("./latex/graphs/comp_two_peak.png")
    #name_png = os.path.join(dir_pngs, f"{out_name}.png")
    name_png = f"{path_result}.png"
    plt.savefig(name_png)
    plt.clf()
    plt.close()
    # plt.show()


def func_lmfit(x, y, config):
    # to do: check for the way to calculate the amplitude from heigth and some fwhm
    # values really seem to need to be adjusted
    def add_peak(x, y, prefix, peak_model, center, range_left, range_right, area_max, area_min, fhwm_max, fhwm_min, **kwargs):
        prefix = f'{prefix}_'
        peak_model = getattr(lmfit.models, peak_model)
        peak = peak_model(prefix=prefix)
        pars = peak.make_params()

        pars[prefix + 'center'].set(center, min=range_left, max=range_right)

        area_max = area_max
        if area_max == 'auto':
            lower = np.searchsorted(x, range_left, 'right')
            upper = np.searchsorted(x, range_right, 'left')
            interval = y[lower:upper]
            print(f'indizes of lower and upper values: {lower}, {upper}')
            # print(interval)
            int_max = max(interval)

            #index_int_max = np.argmax(interval)
            int_min = 0.  # (y - bckg)[lower:upper][index_int_max]
            # print(int_min)
            if int_min < 0.:
                int_min = 0.
            if int_max < 0.:
                int_max = 0.0001
            area_max = (int_max - int_min) * fhwm_max
        area_initial = area_max / 2.
        pars[prefix + 'amplitude'].set(area_initial,
                                       min=area_min, max=area_max)

        # 2.3548 is a tabulated parameter to come from the fwhm to \sigma
        sigma_max = fhwm_max / 2.3548
        sigma_min = fhwm_min / 2.3548

        sigma_initial = (sigma_max - sigma_min) / 2.

        pars[prefix + 'sigma'].set(sigma_initial, min=sigma_min, max=sigma_max)

        if peak_model in ['VoigtModel']:
            pars[prefix + 'gamma'].set(value=sigma_initial,
                                       min=sigma_min, max=sigma_max)
        return peak, pars

    list_model = []
    list_params = []

    rough_peak_positions = config.rough_peak_positions

    keys = rough_peak_positions.keys()
    print(keys)
    for prefix in keys:
        parameterdict_for_the_current_peak = rough_peak_positions.get(prefix)
        range_left = parameterdict_for_the_current_peak.get('range_left')
        range_right = parameterdict_for_the_current_peak.get('range_right')

        if range_right < range_left:
            print("range_right < range_left")
            break
        if not (range_right < x[0]) and not (range_left > x[-1]):
            # TODO: get as starting intensity something like the mean intensity?
            # and as max the max of the whole dataset for each peak?
            center = (range_right - range_left) / 2.
            peak, pars = add_peak(x, y,
                                  prefix, center=center, ** parameterdict_for_the_current_peak)
            list_model.append(peak)
            list_params.append(pars)

    model = list_model[0]
    for part in list_model[1:]:
        model += part
    params = model.make_params()
    for pars in list_params:
        params.update(pars)

    try:
        result = model.fit(
            y, params, x=x, method=config.method_for_fit, max_nfev=config.iterations_max)
    except Exception as e:
        print(f'error in fit:    {e}')
        result = model

    return result
