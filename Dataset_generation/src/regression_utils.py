#import modules
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import bpy
import bpy_extras
import numpy as np
from mathutils import Vector
import random


# import custom modules
from blender_utils import Blender_helper
from dataset_utils import Dataset_helper

class RegressionDatasetGeneration():

    def __init__(self):
        pass

    def get_all_coordinates(self, mesh_name,mesh2class):
        b_box = self.find_bounding_box(bpy.data.objects[mesh_name])

        if b_box:
            return self.format_regression_coordinates(mesh2class[mesh_name], mesh_name)
        
        return ''

    
    def find_bounding_box(self, obj):
        camera_object = bpy.data.objects['Camera']
        matrix = camera_object.matrix_world.normalized().inverted()
        """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
        mesh = obj.to_mesh(preserve_all_data_layers=True)
        mesh.transform(obj.matrix_world)
        mesh.transform(matrix)
        """ Get the world coordinates for the camera frame bounding box, before any transformations. """
        frame = [-v for v in camera_object.data.view_frame(
            scene=bpy.context.scene)[:3]]

        lx = []
        ly = []

        for v in mesh.vertices:
            co_local = v.co
            z = -co_local.z

            if z <= 0.0:
                """ Vertex is behind the camera; ignore it. """
                continue
            else:
                """ Perspective division """
                frame = [(v / (v.z / z)) for v in frame]

            min_x, max_x = frame[1].x, frame[2].x
            min_y, max_y = frame[0].y, frame[1].y

            x = (co_local.x - min_x) / (max_x - min_x)
            y = (co_local.y - min_y) / (max_y - min_y)

            lx.append(x)
            ly.append(y)

        """ Image is not in view if all the mesh verts were ignored """
        if not lx or not ly:
            return None

        min_x = np.clip(min(lx), 0.0, 1.0)
        min_y = np.clip(min(ly), 0.0, 1.0)
        max_x = np.clip(max(lx), 0.0, 1.0)
        max_y = np.clip(max(ly), 0.0, 1.0)

        """ Image is not in view if both bounding points exist on the same side """
        if min_x == max_x or min_y == max_y:
            return None

        """ Figure out the rendered image size """
        render = bpy.context.scene.render
        fac = render.resolution_percentage * 0.01
        dim_x = render.resolution_x * fac
        dim_y = render.resolution_y * fac

        # Verify there's no coordinates equal to zero
        coord_list = [min_x, min_y, max_x, max_y]
        if min(coord_list) == 0.0:
            indexmin = coord_list.index(min(coord_list))
            coord_list[indexmin] = coord_list[indexmin] + 0.0000001

        return (min_x, min_y), (max_x, max_y)

    def get_direction_pca(self, point_cloud):

        cov_matrix = np.cov(point_cloud.T)
        eigen_values, eigen_vectors = np.linalg.eigh(cov_matrix)
        largest_eigen_value = np.argmax(eigen_values)
        eigen_vector_largest = eigen_vectors[:, largest_eigen_value]

        return eigen_vector_largest

    def get_pca_direction_centroid_location(self, obj_name):
        """
        Function returns    PCA data
                            Direction of longitudal axis
                            centroid of the pca
                            location of the object in blender scene.
        """
        # Get the object
        obj = bpy.data.objects[obj_name]
        # Get the camera
        camera_object = bpy.data.objects['Camera']

        # Get the noramlized camera matrix
        matrix = camera_object.matrix_world.normalized().inverted()

        # Get the mesh data of the object object and undo the transformations.
        mesh = obj.to_mesh(preserve_all_data_layers=True)
        mesh.transform(obj.matrix_world)
        mesh.transform(matrix)

        vertices_positions = []
        for v in mesh.vertices:
            vertices_positions.append(list((v.co.x, v.co.y, v.co.z)))

        vertices = np.array(vertices_positions)
        centroid = np.mean(vertices, axis=0)
        direction = self.get_direction_pca(point_cloud=vertices)
        location_object = obj.location

        return vertices_positions, location_object, direction, centroid
    
    def save_point_cloud_data(self,vertices, file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(vertices)

    def project_3d_to_2d(self, vector, view_matrix, projection_matrix):

        x, y, z = vector[0], vector[1], vector[2]

        view_matrix_np = np.array(view_matrix)

        point_3d_homogeneous = np.array([x, y, z, 1])

        # Transform the 3D point to the camera's view space
        point_view = view_matrix_np @ point_3d_homogeneous

        # Apply perspective projection to get 2D image coordinates
        point_projected = projection_matrix @ point_view

        # Convert to normalized device coordinates (NDC)
        point_projected /= point_projected[3]

        # Convert to pixel coordinates
        x_pixel = (point_projected[0] + 1) / 2
        y_pixel = (1 - point_projected[1]) / 2

        return (x_pixel, y_pixel)

    def get_regression_coordinates(self, mesh_name,camera_name):
        """
        Returns the 2d center point and direction vector for the orientation of the object in camera frame.

        """
        # Step1: create object and camera
        object = bpy.data.objects[mesh_name]

        camera = bpy.data.objects['Camera']
        """ Get the world coordinates for the camera frame bounding box, before any transformations. """
        frame = [-v for v in camera.data.view_frame(
            scene=bpy.context.scene)[:3]]

        # 2D center point
        pose_2d = self.project_by_object_utils(bpy.data.objects[str(camera_name)], bpy.data.objects[str(mesh_name)].location)
        
        # Transformation matrix of the object with respect to the world
        T_O_W = object.matrix_world
        
        # Quaternion orientation vector of the object with respect to the world
        Q_O_W = object.rotation_euler.to_quaternion()
        
        # Transformation matrix of the camera with respect to the world
        T_C_W = camera.matrix_world
        print("Direction vector radians : ", np.dot(Q_O_W,np.linalg.inv(T_C_W)))
        # Transformation matrix of the object with respect to the camera: T_O_W * inv(T_C_W)
        direction_vector = [angle+360.0 if angle<0 else angle for angle in np.rad2deg(np.dot(Q_O_W,np.linalg.inv(T_C_W)))]
        
        print("Direction vector degrees : ", direction_vector)
        # bpy.context.object.rotation_mode = 'XYZ'
        
        return pose_2d, direction_vector

    def format_regression_coordinates(self,mesh2class, mesh_name):

        
        scene = bpy.context.scene
        pose_2d, direction_vector = self.get_regression_coordinates(mesh_name,camera_name='Camera')

        pose_2d_x,pose_2d_y = np.array([pose_2d[0], pose_2d[1]])
        # pixel_space = np.array([scene.render.resolution_x, scene.render.resolution_y])
        # pose_2d_x,pose_2d_y = point / pixel_space
        # pose_2d_x,pose_2d_y = point

        # Get distance of object from camera.
        obj_loc = np.array(bpy.data.objects[mesh_name].location)
        cam_loc = np.array(bpy.data.objects['Camera'].matrix_world.decompose()[0][0:3])

        distance = np.linalg.norm(cam_loc-obj_loc)
        print("Distance between the object and camera is : ",distance)
        
        # Formulate line corresponding to the bounding box of one class
        txt_coordinates = {
                        "label": str(mesh2class),
                        "cx": str(pose_2d_x),
                        "cy":str(pose_2d_y),
                        "w": str(direction_vector[0]),
                        "x": str(direction_vector[1]),
                        "y":str(direction_vector[2]),
                        "z":str(direction_vector[3]),
                        "distance": str(distance)
                        }
        print("\nFinal coordinates are : ", txt_coordinates)
        return txt_coordinates

    def project_by_object_utils(self, cam, point):
        point = Vector(point)
        scene = bpy.context.scene
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, point)
        render_scale = scene.render.resolution_percentage / 100
        render_size = (
            int(scene.render.resolution_x * render_scale),
            int(scene.render.resolution_y * render_scale),
        )
        return Vector((co_2d.x * render_size[0], render_size[1] - co_2d.y * render_size[1]))
    
    def get_blender_parameters(self,obj_name,obj_names):

        obj_to_render = bpy.data.objects[str(obj_name)]
        camera = bpy.data.objects['Camera']
        parameters_dict = {}

        parameters_dict['image_path'] = bpy.context.scene.render.filepath
        parameters_dict['obj_name'] = obj_name
        parameters_dict['Total_num_classes'] = len(obj_names)
        parameters_dict['objects_location'] = Dataset_helper().get_location_parameters(
        obj_to_render)
        parameters_dict['objects_rotation'] = Dataset_helper().get_rotation_parameters(
            obj_to_render)
        parameters_dict['light_value'] = bpy.data.lights['Sun'].energy
        parameters_dict['cameras_location'] = {"x":camera.matrix_world.decompose()[0][0],
                                                    "y":camera.matrix_world.decompose()[0][1],
                                                    "z":camera.matrix_world.decompose()[0][2]
                                                    }
        parameters_dict['cameras_rotation'] = {"w":camera.matrix_world.decompose()[1][0],
                                            "x":camera.matrix_world.decompose()[1][1],
                                            "y":camera.matrix_world.decompose()[1][2],
                                            "z":camera.matrix_world.decompose()[1][3]
                                            }
        parameters_dict['focal_length'] = camera.data.lens
        parameters_dict['blur_value'] =camera.data.dof.focus_distance
        parameters_dict['cam_distance_3d'] = camera.constraints['Follow Path'].offset

        return parameters_dict
    
    def write_regression_annotations(self, mesh_name,mesh2class,object_names, json_file_path):

        prameters_dict = self.get_blender_parameters(obj_name=mesh_name,obj_names=object_names)

        print("Mesh name is : ",mesh_name)
        annotations = self.get_all_coordinates(mesh_name,mesh2class)
        print("Annotatons are : ", annotations)

        prameters_dict['annotations'] = annotations

        # Modify to store json files
        with open(json_file_path, "w") as json_file:
            json.dump(prameters_dict, json_file, indent=4)
        
        return None

    def generate_regression_dataset(self,json_object,models_dir,textures_dir,constraint_textures_dir,output_dir,dataset_name):

        OUTPUT_PATH = output_dir
        
        # Create instance for the blender helper class
        blender_helper = Blender_helper()
        dataset_helper = Dataset_helper()

        # Get the parameters list
        parameters = dataset_helper.get_parameters(json_object=json_object)
        print("\n Parameters are : ", parameters)
        print("\n###############################################################################")

        # Get the test cases list
        test_cases = dataset_helper.get_test_cases(json_object=json_object)

        

        # Clear the default scene
        blender_helper.clear_scene()
        # Import objects
        blender_helper.import_objects_obj_format(models_dir=models_dir, 
                                                 target_object_size=0.5, 
                                                 dataset_name=dataset_name)
        
        background_plane, light_source, camera, camera_track, light_track = blender_helper.add_regression_scene()

        obj_names = blender_helper.get_object_names(background_plane_name='Background_plane',
                                                    camera_track='camera_track',
                                                    light_track='light_track'
                                                    )


        print("Number of objects present in the scene are : ", len(obj_names))

        parameters_dict = {}

        num_objects = len(obj_names)
        obj_renders_per_split = Dataset_helper().get_object_render_per_split(json_object)
        total_render_count = sum([num_objects*r[1] for r in obj_renders_per_split])
        
        # Set render parameters:
        render_parameters = json_object.get('render_parameters',{})
        blender_helper.set_render_parameters(device=render_parameters.get("device","CPU"),
                                             render_engine=render_parameters.get("render_engine","CPU"),
                                             res_x=int(render_parameters.get("res_x","96")),
                                             res_y=int(render_parameters.get("res_y","96")) ,
                                             num_samples=int(render_parameters.get("num_samples","100"))
                                             )
        # Set the material
        material = None
        
        
        # Dictionary for class names to mesh
        class_to_idx = {value: key for key, value in enumerate(obj_names)}
        print("Class to index values : ", class_to_idx)

        
        print("***************************  Rendering the images  ***************************")

        # Set all objects to be hidden initially while rendering.
        blender_helper.hide_objects(obj_names=obj_names, hide=True)
        
        # Create start index for the images and starting time
        start_time = time.time()

        for test_case, renders_per_object in obj_renders_per_split:
            print("\n\n Test case is : ", test_case)
            print(f'Starting split: {test_case} | Total renders: {renders_per_object * num_objects}')
            print('**'*30)

            if test_case == 'lighting':
                light_sequential_values = dataset_helper.get_sequential_step_values(test_case,num_elements=renders_per_object,json_object=json_object)
            elif test_case == 'distance':
                distance_sequential_values = dataset_helper.get_sequential_step_values(test_case,num_elements=renders_per_object,json_object=json_object)
            elif test_case == 'blur':
                blur_sequential_values = dataset_helper.get_sequential_step_values(test_case,num_elements=renders_per_object,json_object=json_object)
            else:
                pass
            
            material = blender_helper.set_random_pbr_img_textures(textures_path=textures_dir, obj_name='Background_plane', scale=2.5)
            

            for obj_name in obj_names:
                print(f'Starting object: {test_case}/{obj_name}')
                print('--'*30)

                # get the object and make it visible during rendering.
                obj_to_render = blender_helper.get_object(obj_name=obj_name)
                obj_to_render.hide_render = False

                # Reset the location and rotation of the object
                blender_helper.reset_obj_location_rotation(obj=obj_to_render)

                # Adjust the position of the objects to be above the plane.
                blender_helper.adjust_object_position(obj=obj_to_render,
                                                      target_size=0.1,
                                                      background_plane='Background_plane')
                
                # Track the camera object
                blender_helper.track_object(
                    tracking_object_name='Camera', object_to_track=background_plane) # spanch2s check later for random placement

                # Track the light to the object
                blender_helper.track_object(
                    tracking_object_name='Sun', object_to_track=obj_to_render)

                blender_helper.set_random_rotation(obj_to_change=obj_to_render)
                
                start_idx = 0
                # Loop though number of images to render and render the images.
                for i in range(start_idx, start_idx+renders_per_object):
                    
                    if str('random_rotation_object') in parameters:
                        blender_helper.set_random_rotation(obj_to_change=obj_to_render)

                    if str('random_placement_object') in parameters:
                        blender_helper.random_placement(obj=obj_to_render,camera=camera,min_distance_factor=0.1)

                    if str('random_color') in parameters:
                        blender_helper.set_random_background_color(
                            obj_name='Background_plane')
                    elif str('random_textures') in parameters:
                        material = blender_helper.set_random_pbr_img_textures(
                            textures_path=textures_dir, obj_name='Background_plane', scale=2.5)

                    if test_case == 'normal_training':
                        if json_object['Test_cases'][str(test_case)]['light_parameters']['random_lighting']=='True':
                            light_min,light_max = float(json_object['Test_cases'][str(test_case)]['light_parameters']['min_value']),float(json_object['Test_cases'][str(test_case)]['light_parameters']['min_value'])
                            blender_helper.set_random_lighting(light_source_name='Sun', min_value=light_min, max_value=light_max)
                        else:
                            bpy.data.lights[str('Sun')].energy = 3.0

                        if json_object['Test_cases'][str(test_case)]['distance_parameters']['random_distance']=='True':
                            distance_min,distance_max = float(json_object['Test_cases'][str(test_case)]['distance_parameters']['min_value']),float(json_object['Test_cases'][str(test_case)]['distance_parameters']['min_value'])
                            blender_helper.set_camera_postion_on_path(camera_name='Camera',
                                                                  distance_value = random.uniform(distance_min,distance_max)
                                                                  )
                        else:
                            camera.constraints['Follow Path'].offset = -38
                    
                    elif test_case == 'lighting':
                        bpy.data.lights['Sun'].energy = light_sequential_values[i]
                        blender_helper.set_camera_postion_on_path(camera_name='Camera',
                                                                  distance_value=-38
                                                                  )

                    elif test_case == 'distance':
                        blender_helper.set_camera_postion_on_path(camera_name='Camera',
                                                                  distance_value = distance_sequential_values[i]
                                                                  )
                        bpy.data.lights['Sun'].energy = 3.0

                    elif test_case == 'blur':
                        bpy.data.lights['Sun'].energy = 3.0
                        blender_helper.set_camera_postion_on_path(camera_name='Camera',
                                                                  distance_value=-38
                                                                  )
                        blender_helper.add_blur_dof(blur_value=blur_sequential_values[i],focus_background_name='Background_plane')

                    print(f'\nRendering image {i +1} of {total_render_count}')

                    folder_name = str(dataset_name)+'_'+str(test_case)

                    # Update file path and render
                    bpy.context.scene.render.filepath = str(OUTPUT_PATH / folder_name / obj_name / 'images' / f'{str(i).zfill(6)}.png')
                    bpy.ops.render.render(write_still=True) # RENDER THE IMAGE

                    json_folder = str(OUTPUT_PATH / folder_name / obj_name / f'json_files')
                    if not os.path.exists(json_folder):
                        os.mkdir(json_folder)
                    json_file_path = os.path.join(json_folder, str(f'{str(i).zfill(6)}.json'))    
                    
                    # Save the blender parameters and write the regression annotations
                    self.write_regression_annotations(mesh_name=obj_name,mesh2class=class_to_idx,object_names=obj_names,json_file_path=json_file_path)

                    if str('random_textures') in parameters:
                        if material != None:
                            bpy.data.materials.remove(material)
                        else:
                            pass

                    # Set the blur value back to normal ie, turn off depth of field
                    camera.data.dof.use_dof = False
                # Hide the object again so that it will not appear in the next iteration.
                obj_to_render.hide_render = True
            # Update the starting index
            start_idx += renders_per_object
        
        return None
    
    def count_directories_with_obj_files(self,root_dir):
        count = 0
        for root, dirs, files in os.walk(root_dir):
            # Iterate through all files in the current directory
            for file in files:
                # Check if the file is an OBJ file
                if file.endswith(".obj"):
                    count+=1
        return count
    
