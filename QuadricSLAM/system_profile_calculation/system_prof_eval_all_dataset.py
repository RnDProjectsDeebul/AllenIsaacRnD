"""
This script is used to record the system profile details such as
average RAM and CPU usage for a enitre datasets in a folder.

This file has to be run within the conda environment in which the quadricslam is installed.

change the script_path to the folder containing quadricslam_examples

change the data_path to the folder containing all the datasets

change the optimization mode to run in batch and in incremental mode

run the code multiple times to get an accurate value

And when running this code to monitor the system profile, comment out the ouput file
generation in the quadricslam so that the time not spent on slam can be avoided.

usage:

conda activate quadricslam
python3 system_prof_eval_all_dataset.py
"""

import subprocess
import psutil
import time
import os

# Script path is the main file that should be runned to execute the quadric slam
script_path = '/home/allen/anaconda3/envs/quadricslamtest/lib/python3.10/site-packages/quadricslam_examples/BOP_YCB_dataset_test.py'
# path to the folder containing the datasets
data_path = '/home/allen/Desktop/RnD_Github/AllenIsaacRnD/dataset/'
# extract all the dataset folder names
datasets = []
# Get a list of all items (files and directories) in the folder
items = os.listdir(data_path)
# Filter out only the directories from the list
directories = [item for item in items if os.path.isdir(os.path.join(data_path, item)) and not item.startswith('.')]
directories.sort()
for directory in directories:
    datasets.append(data_path + directory)

# specify batch or incremental optimisaion
batch_optimization = "False"


# Initialize global variables for saving
global_cpu_percent_list = []
global_ram_usage_list = []

for i in range(len(datasets)):

    # Initialize variables for monitoring
    cpu_percent_list = []
    ram_usage_list = []

    # Run the Python script with arguments in a subprocess
    process_sub = subprocess.Popen(['python3', script_path, datasets[i], batch_optimization])
    # Get the PID of the process
    process_pid = process_sub.pid
    # print(f"Process PID: {process_pid}")
    # to get information on the process using its PID
    process = psutil.Process(process_pid)

    #num_cores = psutil.cpu_count(logical=False)

    start_time = time.time() # RECORD THE START TIME

    # Monitor until the process dies
    while process_sub.poll() is None:
        # Monitor CPU utilization
        cpu_percent_list.append(process.cpu_percent(interval=1)/8)
        # Monitor RAM utilization
        ram_usage_list.append(process.memory_info().rss)
        

    end_time = time.time() # RECORD THE END TIME

    execution_time = end_time - start_time # time taken to run

    cpu_percent_list = cpu_percent_list[2:-2] # ignore the initial and final CPU usages that are outliers
    ram_usage_list = ram_usage_list[2:-2] # ignore the initial and final RAM usages that are outliers
    divisor = 1024 * 1024
    ram_usage_list = [element / divisor for element in ram_usage_list] # Convert from bytes to MB

    # remove the RAM recordings giving approximately 0 MB memory usage
    indices_to_remove = [index for index, value in enumerate(ram_usage_list) if value < 2]
    ram_usage_list = [value for index, value in enumerate(ram_usage_list) if index not in indices_to_remove]
    cpu_percent_list = [value for index, value in enumerate(cpu_percent_list) if index not in indices_to_remove]

    # remove the CPU recordings giving approximately 0 % CPU usage
    indices_to_remove = [index for index, value in enumerate(cpu_percent_list) if value < 2]
    ram_usage_list = [value for index, value in enumerate(ram_usage_list) if index not in indices_to_remove]
    cpu_percent_list = [value for index, value in enumerate(cpu_percent_list) if index not in indices_to_remove]


    # save in the global variables
    global_cpu_percent_list.append(cpu_percent_list)
    global_ram_usage_list.append(ram_usage_list)


    # Calculate average CPU and RAM utilization
    average_cpu_utilization = sum(cpu_percent_list) / len(cpu_percent_list)
    average_ram_utilization = sum(ram_usage_list) / len(ram_usage_list)

    print(f"Dataset: {datasets[i]}")
    print(f"Process PID: {process_pid}")
    print(f"Average CPU Utilization: {average_cpu_utilization:.2f}%")
    print("Min and Max CPU Utilization: ", min(cpu_percent_list), max(cpu_percent_list))
    print(f"Average RAM Utilization: {average_ram_utilization:.2f} MB")
    print("Min and Max RAM Utilization: ", min(ram_usage_list), max(ram_usage_list))
    print(f"Total Execution Time: {execution_time:.2f} seconds")
