# import modules
import os
import sys

import bpy
from mathutils import Vector

import random
import math
from math import radians,tan,cos,sin

import re
import json

import numpy as np
from pathlib import Path

#sys.path.append(os.getcwd())

class ObjectDetectionBop:
    
    def __init__(self,background_plane_name,camera_name,light_name,empty_name):
        """
        
        Keyword arguments:
            background_plane_name : str
            camera_name: str
            light_name: str
            empty_name: str
        """
        self.background_plane_name = background_plane_name
        self.camera_name = camera_name
        self.light_name = light_name
        self.empty_name = empty_name
        
        self.clear_scene()

        self.scene = bpy.data.scenes['Scene']


        # For depth images
        self.scene.use_gravity = True
        self.scene.view_layers['ViewLayer'].use_pass_z= True
        self.scene.view_layers['ViewLayer'].use_pass_mist = True


    def add_empty_axis(self,name:str):
        """
        Add a Plain Axis from the empty objects at the origin
        """
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0),rotation=(0, 0, 0))
        self.scene.objects['Empty'].name = str(name)
        return self.scene.objects[str(name)]
    

    def add_camera(self,camera_name: str):
        """
        Add a camera to the origin of the scene 

        Keyword arguments:
            camera_name -- Name for the camera: str 
        """
        bpy.ops.object.camera_add(
            location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
        bpy.context.object.data.lens = 50
        bpy.context.object.data.name = str(camera_name)
        self.scene.camera = bpy.context.object
        return self.scene.objects[str(camera_name)]
    
    def add_light_source(self,Type: str, obj_name: str, shadow: bool):
        """
        Add a light source with respective type to the origin of the scene.

        Keyword arguments:
            type -- The type of light source, default SUN, other: POINT,AREA,SPOT
            obj_name -- Name for the object: str
            shadow -- Enable or Disable shadows: bool

        returns: Light object
        """
        bpy.ops.object.light_add(
            type=str(Type).upper(), radius=1, location=(0, 0, 0))
        bpy.context.object.data.name = str(obj_name)
        bpy.context.object.data.energy = 5
        bpy.context.object.data.use_shadow = shadow
        bpy.context.object.data.use_contact_shadow = shadow
        return self.scene.objects[str(obj_name)]
    
    def set_light_intensity(self,light_name:str,intensity_value:float):
        """
        Set the energy value for the light object.

        Keyword arguments:
            light_name:str
            intensity_value: float
        """
        
        self.scene.objects[light_name].data.energy = intensity_value

    
    def add_background_plane(self,plane_size, name):
        """
        Add the background plane to the scene.

        Keyword arguments:
            plane_size -- size of the plane:float 
            name -- name for the plane :str
        """
        bpy.ops.mesh.primitive_plane_add(
            size=plane_size, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        self.scene.objects['Plane'].name = name
        return self.scene.objects[str(name)]

    def set_location(self,obj_name,location:tuple):
        """
        Set the location of the object

        Keyword arguments:
            obj_name -- Name of the mesh object: str 
            location -- tuple(float,float,float)
        """
        self.scene.objects[str(obj_name)].location = location

    def set_rotation(self,obj_name,rotation):
        """
        Set the rotation of the object

        Keyword arguments:
            obj_name -- Name of the mesh object: str 
            rotation -- tuple(float,float,float)
        """
        self.scene.objects[str(obj_name)].rotation_euler = rotation

    def clear_scene(self):
        """
        Clear the default scene of blender
        """
        # Delete all objects
        bpy.data.objects.remove(bpy.data.objects['Cube'])

        # Delete all cameras
        for camera in bpy.data.cameras:
            bpy.data.cameras.remove(camera)

        # Delete all lights
        for light in bpy.data.lights:
            bpy.data.lights.remove(light)

        return None

    def add_object_detection_scene(self,plane_size:float,camera_z_location:float,axis_x_rotation:float):
        """
        Add basic setup like, camera, light,empty_axis and floor for the objects

        Keyword arguments:
            plane_size -- size of the background plane: float
            camera_z_location-- value of z coordinate: float
            axis_x_rotation --  value for the x rotation: float  
        """

        # add background plane
        background_plane = self.add_background_plane(
            plane_size=plane_size, name=self.background_plane_name)

        # add light source and set it to desired place
        light_source = self.add_light_source(
            Type='sun', obj_name=self.light_name, shadow=True)

        # add camera and set it to desired place
        camera = self.add_camera(camera_name=self.camera_name)

        # add empty axis
        axis = self.add_empty_axis(name=self.empty_name)

        self.set_location(obj_name=self.camera_name,location=(0.0,0.0,camera_z_location))
        # # Set camera as a parent to the main axis.
        # self.scene.objects[self.camera_name].parent = self.scene.objects[self.empty_name]
        # self.set_rotation(obj_name=self.empty_name,rotation=(axis_x_rotation,0.0,0.0))

        return background_plane,light_source,camera,axis
    
    def get_circle_points(self,radius,location,num_points):
        
        ## reducing size by 10 numbers so that 10 more frames can be added at end.
        num_points = num_points - 100
        
        center_point = np.array(location)
        theta_values = np.linspace(0, 2*np.pi, num_points)  # Angle values between 0 and 2*pi
        circle_points = center_point + radius * np.column_stack((np.cos(theta_values), np.sin(theta_values), np.zeros(num_points)))
        
        ### Adding 10 initial frames to the end
        circle_points = np.vstack((circle_points, circle_points[:100]))

        return circle_points
    
    def get_texture_map_paths(self,texture_folder):
        """
        Returns paths for the images which can be used for image textures.

        Keyword arguments:
            texture_folder-- Path for the folder containing the images.
        """
        texture_dict = {
            "normal_map": None,
            "base_color": None,
            "disp_map": None,
            "metal_map": None,
            "roughness_map": None
        }

        files = os.listdir(path=texture_folder)
        for file in files:
            # Match the files and seperate
            nrm_match = re.search(r'\wnormal', file) or re.search(
                r'\wNRM', file) or re.search(r'\wnor', file)
            base_match = re.search(r'\wbasecolor', file) or re.search(
                r'\wCOL_VAR1', file) or re.search(r'\wdiff', file) or re.search(r'\wcol', file)
            disp_match = re.search(r'\wDISP_4K', file) or re.search(
                r'\wheight', file) or re.search(r'\wdisplacement', file) or re.search(r'\wdisp', file)
            metal_match = re.search(r'\wmetallic', file) or re.search(
                r'\wREFL', file) or re.search(r'\wmetal', file)
            rough_match = re.search(r'\wroughness', file) or re.search(
                r'\wGLOSS', file) or re.search(r'\wrough', file)

            if nrm_match:
                normal_map = os.path.join(texture_folder, file)
                texture_dict['normal_map'] = normal_map

            if base_match:
                base_color = os.path.join(texture_folder, file)
                texture_dict['base_color'] = base_color
            if disp_match:
                disp_map = os.path.join(texture_folder, file)
                texture_dict['disp_map'] = disp_map
            if metal_match:
                metal_map = os.path.join(texture_folder, file)
                texture_dict['metal_map'] = metal_map
            if rough_match:
                roughness_map = os.path.join(texture_folder, file)
                texture_dict['roughness_map'] = roughness_map
        return texture_dict

    def get_texture_paths(self,texture_dir):
        """
        Gets the paths for all the texture_folders from the main textures folder and returns them as a list

        Keyword arguments:
            texture_dir-- path for the directory containig the textures.
        """
        bnames = os.listdir(texture_dir)
        for i, cs in enumerate(zip(*bnames)):
            if len(set(cs)) != 1:
                break
        for _i, cs in enumerate(zip(*[b[::-1] for b in bnames])):
            if len(set(cs)) != 1:
                break
        texture_paths = [os.path.join(texture_dir, bname+'/')
                            for bname in bnames if not bname.endswith('.md')]
        return texture_paths

    def set_random_pbr_img_textures(self,textures_path, obj_name, scale):
        """
        Applies image textures randomly from the available images to the specified object.

        Keyword arguments:
            texture_paths-- list of paths for the texture folders.
            obj_name-- name of the object to change the materail/texture
        """

        texture_paths = self.get_texture_paths(textures_path)
        # print("Texture paths : ",texture_paths)
        texture_path = random.choice(texture_paths)

        material_name = str(texture_path.split('/')[-2])
        texture_dict = self.get_texture_map_paths(texture_folder=texture_path)

        # create a new material with the name.
        material = bpy.data.materials.new(
            name=material_name)  # Change name everytime
        material.use_nodes = True

        # Create the nodes for the material

        # Nodes for controlling the texture
        texture_coordinate = material.node_tree.nodes.new(
            type="ShaderNodeTexCoord")
        mapping_node = material.node_tree.nodes.new(type="ShaderNodeMapping")
        mapping_node.inputs['Scale'].default_value = (
            scale, scale, scale)  # Control the scale of the texture

        # Create vector nodes
        normal_map = material.node_tree.nodes.new(type="ShaderNodeNormalMap")
        displacement_map = material.node_tree.nodes.new(
            type="ShaderNodeDisplacement")
        bump_map = material.node_tree.nodes.new(type="ShaderNodeBump")
        invert_node = material.node_tree.nodes.new(type="ShaderNodeInvert")

        # Nodes for principled bsdf and output
        principled_bsdf = material.node_tree.nodes['Principled BSDF']
        material_output = material.node_tree.nodes['Material Output']

        # Connect the nodes
        material.node_tree.links.new(
            texture_coordinate.outputs['UV'], mapping_node.inputs['Vector'])
        # Nodes for image textures
        # Base color
        if texture_dict['base_color'] != None:
            base_color_img = material.node_tree.nodes.new(
                type="ShaderNodeTexImage")
            base_color_img.image = bpy.data.images.load(
                texture_dict['base_color'])
            material.node_tree.links.new(
                mapping_node.outputs['Vector'], base_color_img.inputs['Vector'])
            material.node_tree.links.new(
                base_color_img.outputs['Color'], principled_bsdf.inputs['Base Color'])

        # Normal map
        if texture_dict['normal_map'] != None:
            normal_img = material.node_tree.nodes.new(
                type="ShaderNodeTexImage")
            normal_img.image = bpy.data.images.load(texture_dict['normal_map'])
            material.node_tree.links.new(
                mapping_node.outputs['Vector'], normal_img.inputs['Vector'])
            material.node_tree.links.new(
                normal_img.outputs['Color'], normal_map.inputs['Color'])
            material.node_tree.links.new(
                normal_map.outputs['Normal'], principled_bsdf.inputs['Normal'])

        # Displacement map
        if texture_dict['disp_map'] != None:
            displacement_img = material.node_tree.nodes.new(
                type="ShaderNodeTexImage")
            displacement_img.image = bpy.data.images.load(
                texture_dict['disp_map'])
            material.node_tree.links.new(
                mapping_node.outputs['Vector'], displacement_img.inputs['Vector'])
            material.node_tree.links.new(
                displacement_img.outputs['Color'], displacement_map.inputs['Height'])
            material.node_tree.links.new(
                displacement_map.outputs['Displacement'], material_output.inputs['Displacement'])

        # Roughness map
        if texture_dict['roughness_map'] != None:
            roughness_img = material.node_tree.nodes.new(
                type="ShaderNodeTexImage")
            roughness_img.image = bpy.data.images.load(
                texture_dict['roughness_map'])
            material.node_tree.links.new(
                mapping_node.outputs['Vector'], roughness_img.inputs['Vector'])
            material.node_tree.links.new(
                roughness_img.outputs['Color'], invert_node.inputs['Color'])
            material.node_tree.links.new(
                invert_node.outputs['Color'], principled_bsdf.inputs['Roughness'])

        # Metal map
        if texture_dict['metal_map'] != None:
            metallic_img = material.node_tree.nodes.new(
                type="ShaderNodeTexImage")
            metallic_img.image = bpy.data.images.load(
                texture_dict['metal_map'])
            material.node_tree.links.new(
                mapping_node.outputs['Vector'], metallic_img.inputs['Vector'])
            material.node_tree.links.new(
                metallic_img.outputs['Color'], principled_bsdf.inputs['Metallic'])

        # Set material final output
        material.node_tree.links.new(
            principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])

        # Set the material to the object
        obj = self.scene.objects[obj_name]

        if obj.data.materials:
            obj.data.materials.append(material)
            obj.active_material = bpy.data.materials[material_name]
        else:
            obj.data.materials.append(material)
            obj.active_material = material

        return material
    
    def get_object_names(self,background_plane_name,camera_name,light_name,empty_name):
        """
        Create list of object names present in the scene.

        Keyword arguments:
            background_plane_name--name of the background plane object: str
            camera_name : str
            light_name: str
            empty_name: str
        """

        obj_names = self.scene.objects.keys()

        obj_names.remove(str(background_plane_name))
        obj_names.remove(str(camera_name))
        obj_names.remove(str(light_name))
        obj_names.remove(str(empty_name))

        return sorted(obj_names)
    
    def set_render_parameters(self,device, render_engine, res_x, res_y, num_samples):
        """Sets the active scene with the specified render parameters.

        Keyword arguments:
            device-- Type of the device CPU or GPU : str
            res_x-- resolution width of the image to render: int
            res_y-- resolution height of the image to render: int
            num_samples-- number of render samples 
        """

        self.scene.render.engine = str(render_engine)
        self.scene.cycles.device = str(device).upper()
        self.scene.render.resolution_x = int(res_x)
        self.scene.render.resolution_y = int(res_y)
        self.scene.render.resolution_percentage = 100
        bpy.context.scene.cycles.samples = num_samples
        self.scene.render.image_settings.file_format = "PNG"
    
    def render_image(self,file_path):
        """
        Render the image and save it to the desired location

        Keyword arguments: Complete path: str, eg: path/folder/image_name.png
        """

        self.scene.render.filepath =  file_path
        # Take picture of current visible scene
        bpy.ops.render.render(write_still=True)

    def import_ycb_objects_with_dimensions(self,models_dir,dimensions_dict,class_to_index):
        """
        adds objects from cad format(.obj format) along with their materials.

        Keyword arguments:
            models_dir: path for the models
            dimensions_dict: json object for models dimensions
            class_to_index: dict {class names:idx}, eg: {'cracker_box':2,etc...}
        """
        scene = self.scene
        object_names = []
        obj_files = []
        # Iterate through all subdirectories in the base path
        for root, dirs, files in os.walk(models_dir):
            # Iterate through all files in the current directory
            for file in files:
                # Check if the file is an OBJ file
                if file.endswith(".obj"):
                    # Construct the full path to the OBJ file
                    object_file = os.path.join(root, file)
                    obj_files.append(object_file)

        # Clear the scene
        # bpy.ops.wm.read_factory_settings()
        # self.clear_scene()
        for idx, object_file in enumerate(obj_files):

            obj_name = "".join(object_file.split('/')[-3].split('_')[1::])
            obj_key = class_to_index[obj_name]

            # Import the OBJ file
            bpy.ops.import_scene.obj(filepath=object_file)

            # Set the active object to the imported object
            imported_object = bpy.context.selected_objects[-1]
            # Rename the new object
            imported_object.name = str(obj_name)
            object_names.append(imported_object.name)

            if imported_object is not None:
                # Get the maximum dimension of the object
                imported_object.dimensions.x = float(dimensions_dict[obj_key]["size_x"])*0.001 # Convert mm to meters
                imported_object.dimensions.y = float(dimensions_dict[obj_key]["size_y"])*0.001
                imported_object.dimensions.z = float(dimensions_dict[obj_key]["size_z"])*0.001
                # Rotate the objects so that they appear in standing pose
                # imported_object.rotation_euler = (-90,0,0)

                # Set the origin of the object to its center
                imported_object.select_set(True)
                bpy.context.view_layer.objects.active = imported_object
                
                bpy.ops.object.origin_set(
                    type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
                
                imported_object.location = (0,0,0)
                imported_object.rotation_euler = (0,0,0)
                
                self.adjust_object_position(obj=imported_object,target_size=0.001)
            else:
                print("Error: Object is None")

        return None
    
    def adjust_object_position(self,obj, target_size):
        """
        moves the objects above the background plane.

        Keyword arguments:
            obj: blender mesh object
            target_size: gap between the object and the background plane. 
        """
        max_dim = np.max(obj.dimensions)
        # lift_distance = (max_dim + target_size) / 2
        obj.location.z = (max_dim/2)+target_size

    def get_object(self,obj_name):
        """
        Returns the object present in the scene.

        Keyword arguments:
            obj_name: name of the object:str
        """
        return self.scene.objects[obj_name]
    
    def place_objects_randomly(self,radius):
        """
        Place objects randomly in a circular arrangement.

        Keyword arguments:
            radius -- radius for the circle : float
        """
        obj_names = self.get_object_names(background_plane_name=self.background_plane_name,
                                                     camera_name=self.camera_name,
                                                     light_name=self.light_name,
                                                     empty_name=self.empty_name
                                                     )
        num_objects = len(obj_names)
        
        angle_increment = 2 * math.pi / num_objects

        # Place objects randomly within the circular layout
        for index, obj_name in enumerate(obj_names):
            obj = self.scene.objects.get(obj_name)
            if obj:
                angle = index * angle_increment
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                # Use object's dimensions to adjust the position
                x += obj.dimensions.x * 0.2
                y += obj.dimensions.y * 0.2

                obj.location = Vector((x, y, obj.location.z))


    def get_k_matrix(self,camera_object):
        """
        Get camera calibration matrix 

        # Based on https://mcarletti.github.io/articles/blenderintrinsicparams/

        Keyword arguments:
            camera_object : blender's camera object
        """
        
        scale = self.scene.render.resolution_percentage / 100
        width = self.scene.render.resolution_x * scale # px
        height = self.scene.render.resolution_y * scale # px
        
        camdata = camera_object.data



        focal = camdata.lens # mm
        sensor_width = camdata.sensor_width # mm
        sensor_height = camdata.sensor_height # mm
        pixel_aspect_ratio = self.scene.render.pixel_aspect_x / self.scene.render.pixel_aspect_y

        if (camdata.sensor_fit == 'VERTICAL'):
            # the sensor height is fixed (sensor fit is horizontal), 
            # the sensor width is effectively changed with the pixel aspect ratio
            s_u = width / sensor_width / pixel_aspect_ratio 
            s_v = height / sensor_height
        else: # 'HORIZONTAL' and 'AUTO'
            # the sensor width is fixed (sensor fit is horizontal), 
            # the sensor height is effectively changed with the pixel aspect ratio
            pixel_aspect_ratio = self.scene.render.pixel_aspect_x / self.scene.render.pixel_aspect_y
            s_u = width / sensor_width
            s_v = height * pixel_aspect_ratio / sensor_height

        # parameters of intrinsic calibration matrix K
        alpha_u = focal * s_u
        alpha_v = focal * s_v
        u_0 = width / 2
        v_0 = height / 2
        skew = 0 # only use rectangular pixels

        K = np.array([
            [alpha_u,    skew, u_0],
            [      0, alpha_v, v_0],
            [      0,       0,   1]
        ], dtype=np.float32)
        # s = intrinsics.skew

        cam_K = K.flatten().tolist()
        return cam_K

    def get_scene_camera_parameters(self,camera_object):
        """
        Creates the scene parameters for the BOP annotations

        Keyword argument:
            camera_object: blender's camera object
        """
            
        # transformation of camera with respect to world.
        T_C_W = np.array(camera_object.matrix_world)
        
        #### NEW MODIFICATION TO ROTATE ####
        ## to rotate along 180 degrees in x axis to make the y axis pointing towards the objects
        rot_x = np.array([[1, 0, 0],
                          [0, -1, 0],
                          [0, 0, -1]])
        T_C_W[:3,:3] = T_C_W[:3,:3] @ rot_x
        #### NEW MODIFICATION TO ROTATE ####

        # transformation of world with respect to camera.
        T_W_C = np.linalg.inv(T_C_W)

        cam_R_w2c = T_W_C[:3, :3].flatten().tolist()
        cam_t_w2c = (T_W_C[:3,3]*1000).flatten().tolist()

        scene_parameters = {"cam_K": self.get_k_matrix(camera_object), 
                            "cam_R_w2c": cam_R_w2c, 
                            "cam_t_w2c": cam_t_w2c,  
                            "depth_scale": 10}

        return scene_parameters

    def calculate_scene_gt_parameters(self,obj_name,camera_object,mesh2class):
        """
        Calculate the ground truth parameters of the object for BOP annotations

        Keyword arguments:
            obj_name -- name of the object:str
            camera_object -- blender's camera object
            mesh2class -- dict of mesh names to index eg: {'cracker_box':2,etc..,}
        """
            
        obj = self.scene.objects[obj_name]

        T_m2w = np.array(obj.matrix_world)
        T_c2w = np.array(camera_object.matrix_world)
        
        #### NEW MODIFICATION TO ROTATE ####
        ## to rotate along 180 degrees in x axis to make the y axis pointing towards the objects
        rot_x = np.array([[1, 0, 0],
                          [0, -1, 0],
                          [0, 0, -1]])
        T_c2w[:3,:3] = T_c2w[:3,:3] @ rot_x
        #### NEW MODIFICATION TO ROTATE ####

        T_m2c = np.dot(np.linalg.inv(T_c2w), T_m2w)
        
        cam_R_m2c = T_m2c[:3, :3].flatten().tolist()
        cam_t_m2c = (T_m2c[:3, 3]*1000).flatten().tolist()

        gt_parameters = {
            "cam_R_m2c":cam_R_m2c,
            "cam_t_m2c":cam_t_m2c,
            "obj_id": int(mesh2class[obj_name]),
            "obj_name": obj_name
        }
        return gt_parameters
    
    def get_scene_gt_parameters(self,object_names,camera_object,mesh2class):
        """
        Get the final ground truth parameters for all the objects present in the scene.
        
        Keyword arguments:
            object_names -- list of object names : [str,str, etc..,]
            camera_object -- blender's camera object
            mesh2class -- dict of mesh names to index eg: {'cracker_box':2,etc..,}
        """

        final_parameters = []
        for obj_name in object_names:
            param = self.calculate_scene_gt_parameters(obj_name=obj_name,camera_object=camera_object,mesh2class=mesh2class)
            final_parameters.append(param)

        return final_parameters

    def get_scene_gt_info_parameters(self,object_names,camera,mesh2class):

        """
        Get scene ground truth parameters for the BOP annotations
        """

        annotations = []
        for obj_name in object_names:
            obj_annotations = self.get_all_coordinates(camera,mesh_name=obj_name,mesh2class=mesh2class)
            annotations.append(obj_annotations)

        return annotations

    def format_coordinates(self,coordinates, mesh_name,mesh2class):

        """
        Format bounding box coordinates in bop format.
        """

        res_x = self.scene.render.resolution_x
        res_y = self.scene.render.resolution_y

        if coordinates:

            ## Change coordinates reference frame
            x1 = (coordinates[0][0])
            x2 = (coordinates[1][0])
            y1 = (1 - coordinates[1][1]) 
            y2 = (1 - coordinates[0][1])
            
            ## Get final bounding box information
            # Calculate the absolute width of the bounding box
            width = (x2-x1)
            # Calculate the absolute height of the bounding box
            height = (y2-y1)
            # Calculate the absolute center of the bounding box
            cx = x1 + (width/2) 
            cy = y1 + (height/2)

            ## Formulate line corresponding to the bounding box of one class top left width and height
            # txt_coordinates = str(_class) + ' ' + str(x1) + ' ' + str(y2) + ' ' + str(width) + ' ' + str(height) + '\n'
            txt_coordinates = {
                "bbox_obj":[x1*res_x,y1*res_y,width*res_x,height*res_y],
                "bbox_visib": [x1,y1,width,height],
                "class_label": int(mesh2class[mesh_name]),
                "class_name": mesh_name
            }
            return txt_coordinates
        # If the current class isn't in view of the camera, then pass
        else:
            pass

    def find_bounding_box(self, obj,camera):
        """
        Returns camera space bounding box of the mesh object.

        Gets the camera frame bounding box, which by default is returned without any transformations applied.
        Create a new mesh object based on self.carre_bleu and undo any transformations so that it is in the same space as the
        camera frame. Find the min/max vertex coordinates of the mesh visible in the frame, or None if the mesh is not in view.
        """

        """ Get the inverse transformation matrix. """
        matrix = camera.matrix_world.normalized().inverted()
        """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
        mesh = obj.to_mesh(preserve_all_data_layers=True)
        mesh.transform(obj.matrix_world)
        mesh.transform(matrix)

        """ Get the world coordinates for the camera frame bounding box, before any transformations. """
        frame = [-v for v in camera.data.view_frame(scene=self.scene)[:3]]

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
        render = self.scene.render
        fac = render.resolution_percentage * 0.01
        dim_x = render.resolution_x * fac
        dim_y = render.resolution_y * fac
        
        ## Verify there's no coordinates equal to zero
        coord_list = [min_x, min_y, max_x, max_y]
        if min(coord_list) == 0.0:
            indexmin = coord_list.index(min(coord_list))
            coord_list[indexmin] = coord_list[indexmin] + 0.0000001

        return (min_x, min_y), (max_x, max_y)

    def get_all_coordinates(self,camera,mesh_name,mesh2class):
        """
        Get all bounding box coordinates
        """
        print("Mesh name is : ", mesh_name)
        b_box = self.find_bounding_box(obj= self.scene.objects[mesh_name],camera=camera)

        if b_box:
            return self.format_coordinates(b_box, mesh_name,mesh2class)

        return ''

    def save_as_json_file(self,annotations_dict,file_path):
            with open(file_path,'w') as file:
                json.dump(annotations_dict, file)

    def get_rotation_values_z(self,num_points:int):
        return np.linspace(0, 360, int(num_points))
    
    def set_camera_rotation(self):

        camera = self.scene.objects[self.camera_name]
        target_location = bpy.data.objects[self.empty_name].location
        direction = target_location - camera.location
        rotation_matrix = direction.to_track_quat('-Z', 'Y')
        camera.rotation_euler = rotation_matrix.to_euler()
    

if __name__ == '__main__':
    
    ###################TESTING GPU###################
    # Set rendering engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'

    # Set rendering device to GPU
    bpy.context.scene.cycles.device = 'GPU'

    # Use all available GPUs for rendering
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.preferences.addons['cycles'].preferences.get_devices()
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    for device in bpy.context.preferences.addons['cycles'].preferences.devices:
        device.use = True
    ###################TESTING GPU###################
    
    
    PARENT_DIR = os.path.normpath(os.getcwd()+os.sep+os.pardir)
    TEXTURES_DIR = os.path.join(PARENT_DIR,'blender_files/constraint_textures/')
    MODELS_DIR = os.path.join(PARENT_DIR,'blender_files/models/sample_models/')
    MODELS_DIM_JSON = os.path.join(PARENT_DIR,'src/models_info.json')

    SAVE_DIR = os.path.join(os.getcwd(),'results/scene3/')

    RGB_DIR = SAVE_DIR+'rgb/'
    DEPTH_DIR = SAVE_DIR+'depth/'
    JSON_DIR = SAVE_DIR
    
    NUM_OF_IMAGES = 1500

    dataset_info = {'1': 'masterchefcan',
                '2': 'crackerbox',
                '3': 'sugarbox',
                '4': 'tomatosoupcan',
                '5': 'mustardbottle',
                '6': 'tunafishcan',
                '7': 'puddingbox',
                '8': 'gelatinbox',
                '9': 'pottedmeatcan',
                '10': 'banana',
                '11': 'pitcherbase',
                '12': 'bleachcleanser',
                '13': 'bowl',
                '14': 'mug',
                '15': 'powerdrill',
                '16': 'woodblock',
                '17': 'scissors',
                '18': 'largemarker',
                '19': 'largeclamp',
                '20': 'extralargeclamp',
                '21': 'foambrick'}
    
    # Dictionary for class names to index
    class_to_idx = {value: key for key, value in dataset_info.items()}
    print("Class to index values : ", class_to_idx)

    #load the json file for models dimension
    with open(MODELS_DIM_JSON,'r') as json_file:
        dimensions_data = json.load(json_file)
    
    # Create instance for object detection class
    detection_helper = ObjectDetectionBop(background_plane_name='Background_plane',
                                          camera_name='Camera',
                                          light_name='Sun',
                                          empty_name='Main_axis')

    # import ycb objects with dimensions
    detection_helper.import_ycb_objects_with_dimensions(models_dir=MODELS_DIR,dimensions_dict=dimensions_data,class_to_index=class_to_idx)
    
    # Add object detection scene.
    detection_helper.add_object_detection_scene(plane_size=5.0,camera_z_location=2.0,axis_x_rotation=45)

    # Set the location of the light object
    detection_helper.set_location(obj_name=detection_helper.light_name,location=(0.0,0.0,3.0))
    detection_helper.set_light_intensity(light_name=detection_helper.light_name,intensity_value=4.0)

    # Set the render parameters.
    detection_helper.set_render_parameters(device='GPU',
                                           render_engine='CYCLES',
                                           res_x=640,
                                           res_y=480,
                                           num_samples=100
                                           )

    # get the object names
    object_names = detection_helper.get_object_names(background_plane_name=detection_helper.background_plane_name,
                                                     camera_name=detection_helper.camera_name,
                                                     light_name=detection_helper.light_name,
                                                     empty_name=detection_helper.empty_name
                                                     )
    print(f"\nObjects present in the scene are {len(object_names)} : {object_names}  ")
    
    # Place the objects randomly in a circular arrangement.
    detection_helper.place_objects_randomly(radius=0.17) # CAN CHANGE
    
    # Set the material for the background plane
    material = None
    # CAN CHANGE THE SCALE OF THE TEXTURE
    material = detection_helper.set_random_pbr_img_textures(textures_path=TEXTURES_DIR,obj_name=detection_helper.background_plane_name,scale=3.0) 

    # Setup compositor for depth images.
    detection_helper.scene.use_gravity = True
    detection_helper.scene.view_layers['ViewLayer'].use_pass_z= True
    detection_helper.scene.view_layers['ViewLayer'].use_pass_mist = True

    detection_helper.scene.use_nodes = True
    tree = detection_helper.scene.node_tree

    if not tree.nodes['Render Layers']:
        render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
    else:
        render_layers_node = tree.nodes['Render Layers']

    if not tree.nodes['Composite']:
        output_node = tree.nodes.new(type='Composite')
    else:
        output_node = tree.nodes['Composite']

    links = tree.links

    # Create dictionaries to store BOP annotations.
    scene_camera_params = {}
    scene_gt_params = {}
    scene_gt_info_params = {}   

    # Main rendering loop !!!!!!
    # circle_points = detection_helper.get_rotation_values_z(num_points=NUM_OF_IMAGES)
    circle_points = detection_helper.get_circle_points(radius=1.2,location=[0.0,0.0,0.3],num_points=NUM_OF_IMAGES) # Radius for the camera path.
    # CAN CHANGE THE Z OF CAMERA AND THE RADIUS OF THE CAMERA
    for idx,loc_value in enumerate(circle_points):
        
        scene = detection_helper.scene
        camera = detection_helper.scene.objects[detection_helper.camera_name]
        
        # Set the rotation of the axis so that the camera will rotate in z axis.
        # detection_helper.scene.objects[detection_helper.empty_name].rotation_euler.z = rot_value
        detection_helper.scene.objects[detection_helper.camera_name].location = loc_value
        detection_helper.set_camera_rotation()

        # Update file path for rgb images and render the image.
        detection_helper.scene.render.filepath = os.path.join(RGB_DIR, str(f"{str(idx).zfill(6)}.png"))
        print("File name of rgb image is  : ", detection_helper.scene.render.filepath)
        links.new(render_layers_node.outputs["Image"], output_node.inputs['Image'])
        bpy.ops.render.render(write_still = True)


        # Store the json labels
        scene_camera_params[str(idx)] = detection_helper.get_scene_camera_parameters(camera_object=camera) 
        scene_gt_params[str(idx)] = detection_helper.get_scene_gt_parameters(object_names=object_names,camera_object=camera,mesh2class=class_to_idx)
        scene_gt_info_params[str(idx)] = detection_helper.get_scene_gt_info_parameters(object_names=object_names,camera=camera,mesh2class=class_to_idx)

        # Create depth images
        detection_helper.scene.render.filepath = os.path.join(DEPTH_DIR, str(f"{str(idx).zfill(6)}.png"))
        print("File name of depth image is  : ", detection_helper.scene.render.filepath)
        links.new(render_layers_node.outputs["Depth"], output_node.inputs['Image'])
        bpy.ops.render.render(write_still = True)

    scene_cam_path = JSON_DIR + 'scene_camera.json'
    scene_gt_path = JSON_DIR + 'scene_gt.json'
    scene_gt_info_path = JSON_DIR + 'scene_gt_info.json'

    detection_helper.save_as_json_file(annotations_dict=scene_camera_params,file_path=scene_cam_path)
    detection_helper.save_as_json_file(annotations_dict=scene_gt_params,file_path=scene_gt_path)
    detection_helper.save_as_json_file(annotations_dict=scene_gt_info_params,file_path=scene_gt_info_path)

    print("************************** Completed Rendering process **************************")
