# import modules
import json
import math
from math import radians,tan,cos,sin
import random
import numpy as np

from blender_utils import Blender_helper


class Dataset_helper:

    def __init__(self) -> None:
        pass

    def get_test_cases(self, json_object):
        """
        This fuction returs the list of test cases for generating different datasets.

        Args: json_object - Json object which contains the data from requirements file.
        return : list(str)
        """

        assert type(
            json_object) == dict, "Json object should be of the form dict"

        test_cases = []
        for item in json_object['Test_cases'].items():
            if json_object['Test_cases'][item[0]]['condition'] == 'True':
                test_cases.append(item[0])
        return test_cases

    def get_parameters(self, json_object):
        """
        This function returns the list of parameters that are used to modify the datasets.

        Args: json_object - Json object which contains the data from requirements file.
        return : list(str)
        """

        assert type(
            json_object) == dict, "Json object should be of the form dict"
        parameters = []
        for item in json_object['Parameters'].items():
            if json_object['Parameters'][item[0]] == 'True':
                parameters.append(item[0])
        return parameters

    def get_min_max_values(self, test_case, json_object):
        """
        This function returns the minimum and maximum values from the json object for the particular test case

        Args:
            test_case: str
            json_object : json_object

        """
        min_value = json_object['Test_cases'][str(test_case)]['min_value']
        max_value = json_object['Test_cases'][str(test_case)]['max_value']

        return float(min_value), float(max_value)

    def get_object_render_per_split(self, json_object):

        test_cases = self.get_test_cases(json_object=json_object)
        num_images_per_class = int(json_object['Num_images_per_class'])
        obj_render_list = []
        for condition in test_cases:
            obj_render_list.append((condition, num_images_per_class))
        return obj_render_list

    def save_as_json_file(self, file_path, parameters_dict):

        with open(str(file_path), 'w', encoding='utf-8') as f:
            json.dump(parameters_dict, f, ensure_ascii=False, indent=4)

        return None

    def get_location_parameters(self, object):

        parameters = {'x': object.location.x,
                      'y': object.location.y,
                      'z': object.location.z}
        return parameters

    def get_rotation_parameters(self, object):

        parameters = {'x': object.rotation_euler.x,
                      'y': object.rotation_euler.y,
                      'z': object.rotation_euler.z}
        return parameters

    def get_sequential_step_values(self, test_case, num_elements,json_object):

        start_value,stop_value = self.get_min_max_values(test_case=test_case,json_object=json_object)

        step_value = (stop_value - start_value) / (num_elements - 1)
        numbers_list = np.arange(
            start_value, stop_value + step_value, step_value)

        return numbers_list
    
    def random_placement(self,obj, camera, fov_degrees=None, min_distance_factor=.5, max_distance_factor=3.0):
        """
        Place a sinlge object randomly in camera view
        """
        # Get the current camera field of view in degrees if not provided
        if fov_degrees is None:
            fov_radians = camera.data.angle
            fov_degrees = math.degrees(fov_radians)
        else:
            fov_radians = radians(fov_degrees)
        
        # Calculate camera height and width for the current FOV
        aspect_ratio = camera.data.sensor_width / camera.data.sensor_height
        camera_height = 2 * camera.location.z * tan(fov_radians / 2)
        camera_width = camera_height * aspect_ratio
        
        object_size_percentage = 0.2
        object_width = object_size_percentage * camera_width

        max_distance = object_width / (2 * tan(fov_radians / 2))
        
        min_distance = min_distance_factor * max_distance
        
        # Calculate random distance within the range
        random_distance = random.uniform(min_distance, max_distance)
        
        # Calculate random angle (azimuth) around the camera
        random_angle = random.uniform(0, 2 * math.pi)
        
        # Calculate the object position relative to the camera
        random_x = random_distance * cos(random_angle)
        random_y = random_distance * sin(random_angle)
        random_z = obj.dimensions.z / 2
        
        # Set the object location
        obj.location = (random_x, random_y, random_z)
