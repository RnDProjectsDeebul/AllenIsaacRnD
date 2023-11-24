import os
import sys
import argparse
import numpy as np
import json
from pathlib import Path
import time
import bpy

# append the working directory so that blender will recognise the custom modules.
sys.path.append('/home/user_name/.local/lib/python3.10/site-packages')
sys.path.append('/home/user_name/ConstraintBasedDatasetGenerator/src/')

# import custom modules 
from dataset_helpers import Dataset_helper
from blender_utils import Blender_helper

print('\nAll modules are sucessfully imported')

# json file path 
json_path = './argument_files/requirements_classification.json'

# read the json file
json_file = open(json_path,'r')
json_data = json_file.read()

# Parse the json data
json_object = json.loads(json_data)

# output_path = Path(str(json_object['output_path']))
num_images_per_class = int(json_object['Num_images_per_class'])


dir_path = os.path.normpath(os.getcwd() + os.sep + os.pardir)

textures_path = os.path.join(dir_path,'blender_files/textures/')
models_path = os.path.join(dir_path,'blender_files/models/Robocup_components/')


dataset_tool = Dataset_helper()
blender_helper = Blender_helper()

obj_names = blender_helper.get_object_names(background_plane_name='Floor')
num_objects = len(obj_names)

obj_renders_per_split = dataset_tool.get_object_render_per_split(json_object,num_images_per_class)

total_render_count = sum([num_objects*r[1] for r in obj_renders_per_split])

print("\nTotal num of images to render : ",total_render_count)


# Accept yes or no from the terminal add it here.
user_input = input("\nEnter \"y\" to continue rendering     or \n      \"n\" to abort the process and modify the parameters \nUser Input :   ")


if user_input == 'y' or 'Y':
    dataset_tool.generate_classification_dataset(json_object=json_object,dataset_name='robocup_')
elif user_input == 'n' or 'N':
    print("Data generation aborted")
else:
    print("Data generation aborted")
    
print("Dataset generation completed successfully")
