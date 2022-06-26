# jabamur
JSON based multi peak refinement

==========
TODOs:

numerate scripts!

Improvement of project structure from scripts to installable module is in progress.

Add full working example.

First big error was that project has not immediately been set up as installable module.

In principle one would only need to define the input and output files for the fitting procedure to run. Most of the macros contain procedures for data preparation.

I see that it is hard to follow. Need to refactor and make the flow more organized!

==========

Was developed for data treatment in:

An In Situ Synchrotron X-Ray Diffraction Study on the Influence of Hydrogen on the Crystallization of Ge-Rich Ge2Sb2Te5 (Philipp Hans, Cristian Mocuta, Marie-Ingrid Richard, Daniel Benoit, Philippe Boivin, Yannick Le-Friec, Roberto Simola, Olivier Thomas) - https://onlinelibrary.wiley.com/doi/10.1002/pssr.202100658


The general project structure that I decided to use is the following:

projects_fitting		
	*.project
		data_for_analysis
			files.npy
			files.bckg.npy
		results
			files.fitresS
			files.png
			files.x_y_bckg.npy
		list_of_files
		*.beads_parameters
		*.json
		*.refine

In principle the most important files are list_of_files and *.refine.
→ “list_of_files” is a ascii file with two columns that contains the paths to the datasets that should be refined and the locations where results should be saved
→ “*.refine” contains the refinement instructions. It is a file in json format with contents (example):

{
    "descriptor": "dummy_descriptor",
    "range_of_interest": [
        1.69,
        2.25
    ],
    "rough_peak_positions" : {
        "GST_cub_111": {"peak_model": "VoigtModel", "range_left": 1.79, "range_right": 1.821, "area_max" : "auto", "area_min": 0.0, "fhwm_max": 0.15, "fhwm_min": 0.0},
        "Ge_111":      {"peak_model": "VoigtModel", "range_left": 1.91, "range_right": 1.93, "area_max" : "auto", "area_min": 0.0, "fhwm_max": 0.15, "fhwm_min": 0.0},
        "GST_trig":    {"peak_model": "VoigtModel", "range_left": 2.048, "range_right": 2.07, "area_max" : "auto", "area_min": 0.0, "fhwm_max": 0.15, "fhwm_min": 0.0},
        "GST_cub_200": {"peak_model": "VoigtModel", "range_left": 2.07, "range_right": 2.09, "area_max" : "auto", "area_min": 0.0, "fhwm_max": 0.15, "fhwm_min": 0.0}
    },
    "overwrite": false,
    "method_for_fit": "differential_evolution",
    "iterations_max": 70000
}
 
The project structure described above is created by the scripts that are provided in the folder “scripts_peakfitting”. They will work for the soleil 2021 july project, where a folder with all integrated files in exemplary format “epoch1626665631.38_pos-5.50_scan_40670.dat” is given (because my scripts filter the files according to the number at the end to copy them an npy-binary format to the project folder).





Below, a routine how to set up a complete refinement (incl creating a suited python environment via conda) is given (see also README_setting_up_system_and_refinements_example.txt):
=========================================================================
### theoretically needs to be run only once

conda create -n py38 python=3.8
conda activate py38

pip install numpy
pip install matplotlib
pip install lmfit
pip install pybaselines
pip install simple_parsing
pip install pandas
pip install joblib
pip install dill

script_create_config_files_as_json .py

mv projects_fitting_/ projects_fitting
cd projects_fitting/
script_setup_projects_from_jsons.py
cd ..

script_create_project-to-refine_json_from_project_folders .py

==========================================================
### can be run multiple times

script_provide_files_structured_according_to_config_file.py
script_estimate_beads_from_config.py
###example for selection of files.py
script_provide_list_of_files_that_should_be_refined.py --first 250 --spacing 10
script_create_and_save_beads_for_list_of_files.py

script_multi_peak_fitting.py --parallel yes --number_of_processes 8 --debug no

script_load_and_process_lmfit_results.py --do_extraction yes
=========================================================================
Working on linux, I decided to place all scripts in a central folder and to add that folder to the PATH variable by the commands export PATH="$HOME/SCRIPTS/scripts_peakfitting/:$PATH" or source add_scripts_to_PATH.sh
(The PATH variable is an environment variable that contains an ordered list of paths that Linux will search for executables when running a command. - It might be possible to set up something similar for windows systems as well). By working with the PATH variable, my procedures would be available in every folder irrespective of the relative location to the script folder (-> means that different projects could be analyzed that way more easily).
For the moment, the scripts are designed to accomplish single peak fits on one range of 1D diffraction data that are specially arranged according to some conventions. Therefore, config-files are used.

In what follows the above steps and also all CONVENTIONS will be explained: To provide the clear arrangement the data to be analyzed are separated from the raw data folder and all designated under the current working directory “.” .

    • The integrated files are initially saved as tth, I(tth) ascii dat files and have a format similar to “epoch1626665631.38_pos-5.50_scan_40670.dat”.

    • For each conducted experiment exist a couple of config files:
        ◦ json: defines e.g. energy and bounds per experiment; data locations; working folder; temperature log files; a unique descriptor
        ◦ beads_parameters: this enables one to determine a background if no suited background was measured or is nevertheless necessary
        ◦ refine: defines all peaks that should be fitted and the kind of algorithm

    • 0 - The procedure (after having created and activated the python environment) will start from a csv-file of the following format:

#sample	descriptor	type of measurement	temperature_program deg C	scans per diffractogram	aquisition time [s]	scan_first	scan_last
S50	S50_ramp	ramp	10 dg/min ->  180; then 2dg/m -> 450; 10 dg/M for cooling	3	5	37	1707
S50	S50_iso_Txm5GST_395_deg_part1	isothermal	395	2	20	1712	3657
S447 POR	S447_ramp	ramp	10 dg/min ->  180; then 2dg/m -> 450; 10 dg/M for cooling	2	5	3665	4868

    • The parameters from that file will be extracted and json files an a folder “projects_fitting_” created. It is named that way with an underscore at the end to prevent data loss. (script_create_config_files_as_json .py)
    • “projects_fitting_” needs to be renamed to “projects_fitting”. Enter the directory, run “script_setup_projects_from_jsons.py” and leave the directory. → A folder that is named after the descriptor in the config file is created (script_setup_projects_from_jsons.py).
    • A file “projects_to_refine.json” needs to be created. It tells the procedure which projects should be refined. (script_create_project-to-refine_json_from_project_folders .py)

    • 1 - All files that belong to an experiment are opened, from X-ray energy and tth the q-axis is calculated. The files are saved as q, I(q) .npy (numpy binray format) files to a new folder "./data_for_analysis/{descriptor}". The npy format can be opened fastly and the filesize is small. (script_provide_files_structured_according_to_config_file.py)

    • 2 – based on a template file “template_beads_parameters.beads_parameters”, a baseline is estimated via the beads approach for each experiment that should be refined. An option to accept the current set of parameters is given. If a {descriptor}.beads_parameters file already exists, background estimation is skipped. (script_estimate_beads_from_config.py).

    • 3 - The amount of data can be very large. To get preliminary results, it can be helpful to analyze only a subset of the data. By means of the descriptor the folder is chosen and by means of first, last, jump the files can be selected systematically. A list of files is created as “./list_of_files/{descriptor}.list_of_files” (script_provide_list_of_files_that_should_be_refined.py --first 250 --spacing 10)

    • 4 - according to the {descriptor}. beads_parameters a background is estimated and saved for all files in “./list_of_files/{descriptor}.list_of_files” if it was not already saved in a previous turn. (script_create_and_save_beads_for_list_of_files.py)

    • 5 - based on the *.refine files the procedure selects which files (experiments) should be refined.

=========================================================================
