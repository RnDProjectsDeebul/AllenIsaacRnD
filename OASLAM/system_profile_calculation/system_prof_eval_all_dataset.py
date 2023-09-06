"""
This script is used to record the system profile details such as
average RAM and CPU usage for all the datasets.


The below command is used to run the oa-slam
./oa-slam
../Vocabulary/ORBvoc.txt -> vocabulary_file
~/Desktop/BOP_dataset_oaslam/ycbv/test/camera_uw.yaml -> camera_file
~/Desktop/BOP_dataset_oaslam/ycbv/test/000048/rgb/ -> path_to_image_sequence (.txt file listing the images or a folder with rgb.txt)
~/Desktop/BOP_dataset_oaslam/ycbv/test/000048/detections_yolov5.json -> detections_file (.json file with detections or .onnx yolov5 weights)
null -> categories_to_ignore_file (file containing the categories to ignore (one category_id per line))
points+objects -> relocalization_mode ('points', 'objects' or 'points+objects')
000048 -> output_name 

run the code multiple times to get an accurate value

Need to change
script_path -> path to the OA-SLAM files
camera_file -> path to the camera intrinsics file
data_path -> path to the dataset

usage:

python3 system_prof_eval_all_dataset.py
"""

import subprocess
import psutil
import time
import os
import shutil

def copy_folder_contents(source_folder, destination_path):
    try:
        # Check if the source folder exists
        if not os.path.exists(source_folder):
            print("Source folder does not exist.")
            return

        # Create the destination folder if it doesn't exist
        os.makedirs(destination_path, exist_ok=True)

        # Loop through each item in the source folder
        for item in os.listdir(source_folder):
            source_item_path = os.path.join(source_folder, item)
            destination_item_path = os.path.join(destination_path, item)

            # If the item is a file, copy it to the destination
            if os.path.isfile(source_item_path):
                shutil.copy2(source_item_path, destination_item_path)
            # If the item is a folder, recursively copy its contents
            elif os.path.isdir(source_item_path):
                shutil.copytree(source_item_path, destination_item_path)

        print("Contents copied successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Script path is the main file that should be runned to execute the oa-slam
script_path = '/home/allen/Desktop/OA_SLAM/oaslam/OA-SLAM/'
bin_path = script_path + 'bin/oa-slam'
orbvoc_path = script_path + 'Vocabulary/ORBvoc.txt'
# path to the camera intrinsics file.
camera_file = '/home/allen/Desktop/RnD_Github/AllenIsaacRnD/dataset/camera_simulator.yaml'
# path to the dataset folders
data_path = '/home/allen/Desktop/RnD_Github/AllenIsaacRnD/dataset/'


# change the current present working directory to identify files with relative paths
os.chdir(script_path+'bin/')

# extract all the dataset folder names
datasets = []
# Get a list of all items (files and directories) in the folder
items = os.listdir(data_path)
# Filter out only the directories from the list
directories = [item for item in items if os.path.isdir(os.path.join(data_path, item)) and not item.startswith('.')]
directories.sort()
for directory in directories:
    datasets.append(data_path + directory)


# Initialize global variables for saving
global_cpu_percent_list = []
global_ram_usage_list = []

for i in range(len(datasets)):

    rgb_path = datasets[i] + '/rgb/'
    yolo_detection_path = datasets[i] + '/detections_yolov5.json'
    output_name = os.path.basename(os.path.normpath(datasets[i]))

    # Initialize variables for monitoring
    cpu_percent_list = []
    ram_usage_list = []

    # Run the Python script with arguments in a subprocess
    process_sub = subprocess.Popen([bin_path, orbvoc_path, camera_file, rgb_path, 
                                    yolo_detection_path, 'null', 'points+objects', output_name])
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


    # Calculate average CPU and RAM utilization
    average_cpu_utilization = sum(cpu_percent_list) / len(cpu_percent_list)
    average_ram_utilization = sum(ram_usage_list) / len(ram_usage_list)

    # save in the global variables
    global_cpu_percent_list.append(cpu_percent_list)
    global_ram_usage_list.append(ram_usage_list)

    print(f"Dataset: {datasets[i]}")
    print(f"Process PID: {process_pid}")
    print(f"Average CPU Utilization: {average_cpu_utilization:.2f}%")
    print("Min and Max CPU Utilization: ", min(cpu_percent_list), max(cpu_percent_list))
    print(f"Average RAM Utilization: {average_ram_utilization:.2f} MB")
    print("Min and Max RAM Utilization: ", min(ram_usage_list), max(ram_usage_list))
    print(f"Total Execution Time: {execution_time:.2f} seconds")
    
    # copy contents of the folder
    copy_folder_contents('./' + output_name, datasets[i] + '/oa_slam_result/')