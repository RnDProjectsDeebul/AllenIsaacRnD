# import modules
import os
import json
import sys
from pathlib import Path

sys.path.append(os.getcwd())

# import custom modules
from dataset_utils import Dataset_helper
from regression_utils import RegressionDatasetGeneration
print('\nAll modules are sucessfully imported')


def main(parent_dir,models_dir,textures_dir,constraint_textures_dir,arguments_file):
    """
    Main rendering code for regression dataset
    """
    json_file = open(arguments_file,'r')
    json_data = json_file.read()
    json_object = json.loads(json_data)

    dataset_name = json_object.get("dataset_name",'ycb')
    if dataset_name == 'ycb':
        models_path = os.path.join(models_dir,'ycb_models/')
    elif dataset_name=='robocup':
        models_path = os.path.join(models_dir,'robocup_models/')
    else:
        raise NameError("Provide valid dataset name -- ycb or robocup")
    
    if str(json_object['output_path']) == "":
        OUTPUT_DIR = Path(os.path.join(parent_dir,'results/'))
    else:
        OUTPUT_DIR = Path(str(json_object['output_path']))
            
    num_objects = RegressionDatasetGeneration().count_directories_with_obj_files(root_dir=models_path)
    obj_renders_per_split = Dataset_helper().get_object_render_per_split(json_object)
    total_render_count = sum([num_objects*r[1] for r in obj_renders_per_split])

    print("*********************************************************************\n")
    print(f"Generating Regression dataset for {dataset_name} objects")
    print("\nNumber of objects per test case and per object : ", obj_renders_per_split)
    print("\nTotal num of images to render : ",total_render_count)
    print("\n*********************************************************************")

    try:
        user_input = input("\nEnter \"y\" to continue rendering or \"n\" to abort the process: ").strip().lower()

        if user_input == "y":
            RegressionDatasetGeneration().generate_regression_dataset(json_object=json_object,
                                                              models_dir=models_path,
                                                              textures_dir=textures_dir,
                                                              constraint_textures_dir=constraint_textures_dir,
                                                              output_dir = OUTPUT_DIR,
                                                              dataset_name=dataset_name
                                                              )
        else:
            print("Aborted the process.")

    except KeyboardInterrupt:
        print("\nProcess aborted by user (Ctrl+C).")


    return None


if __name__ == '__main__':
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
    PARENT_DIR = os.path.normpath(os.getcwd()+os.sep+os.pardir)
    MODELS_DIR = os.path.join(PARENT_DIR,'blender_files/models/')
    TEXTURES_DIR = os.path.join(PARENT_DIR,'blender_files/textures/')
    CONSTRAINT_TEXTURES_DIR = os.path.join(PARENT_DIR,'blender_files/constraint_textures/')
    ARGS_FILE = os.path.join(PARENT_DIR,'argument_files/requirements_regression.json')
    
    main(parent_dir=PARENT_DIR,
         models_dir=MODELS_DIR,
         textures_dir=TEXTURES_DIR,
         constraint_textures_dir=CONSTRAINT_TEXTURES_DIR,
         arguments_file=ARGS_FILE
         )

