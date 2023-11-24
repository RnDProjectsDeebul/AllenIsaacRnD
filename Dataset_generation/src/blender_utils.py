import math
import os
import random
import re

import bpy
from mathutils import Color, Euler, Vector
import numpy as np
from math import radians,tan,cos,sin

class Blender_helper:

    def __init__(self) -> None:
        pass

    def clear_scene(self):
        # Clear existing objects
        # Delete all objects
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()

        # Delete all materials
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)

        # Delete all cameras
        for camera in bpy.data.cameras:
            bpy.data.cameras.remove(camera)

        # Delete all lights
        for light in bpy.data.lights:
            bpy.data.lights.remove(light)

        # Delete all curves (bezier circles, etc.)
        for curve in bpy.data.curves:
            bpy.data.curves.remove(curve)

        # Delete all images
        for image in bpy.data.images:
            bpy.data.images.remove(image)

        # Delete all textures
        for texture in bpy.data.textures:
            bpy.data.textures.remove(texture)

        # Delete all nodes in node trees
        for material in bpy.data.materials:
            if material.use_nodes:
                material.node_tree.nodes.clear()

        # Delete all node groups
        for node_group in bpy.data.node_groups:
            bpy.data.node_groups.remove(node_group)

        return None

    def add_basic_scene(self):
        """
        This function adds  basic setup like, camera, light and floor for the objects

        use the functions below
        """

        # add background plane
        background_plane = self.add_background_plane(
            plane_size=5, name='Background_plane')

        # add light source and set it to desired place
        light_source = self.add_light_source(
            type='sun', obj_name='Sun', shadow=True)

        # add camera and set it to desired place
        camera = self.add_camera(camera_name='Camera')

        # add curves for following the path
        camera_track = self.add_beizer_curve(
            name='camera_track', location=(0, 0, 2.5), scale=(0, 0, 0))
        light_track = self.add_beizer_curve(
            name='light_track', location=(0, 0, 3), scale=(0, 0, 0))

        # Set the follow path constraints
        camera.constraints.new(type='FOLLOW_PATH')
        camera.constraints['Follow Path'].target = camera_track

        light_source.constraints.new(type='FOLLOW_PATH')
        light_source.constraints['Follow Path'].target = light_track

        return background_plane, light_source, camera, camera_track, light_track
    
    def add_regression_scene(self):
        # add background plane
        background_plane = self.add_background_plane(
            plane_size=5, name='Background_plane')

        # add light source and set it to desired place
        light_source = self.add_light_source(
            type='sun', obj_name='Sun', shadow=True)

        # add camera and set it to desired place
        camera = self.add_camera(camera_name='Camera')

        # add curves for following the path
        light_track = self.add_beizer_curve(
            name='light_track', location=(0, 0, 3), scale=(0, 0, 0))
        light_source.constraints.new(type='FOLLOW_PATH')
        light_source.constraints['Follow Path'].target = light_track

        camera_track = self.add_nurbs_path(name='camera_track')
        camera.constraints.new(type='FOLLOW_PATH')
        camera.constraints['Follow Path'].target = camera_track


        return background_plane, light_source, camera, camera_track, light_track
    
    def add_nurbs_path(self, name):
        bpy.ops.curve.primitive_nurbs_path_add(enter_editmode=False,align='WORLD',location=(0, 0, 1),rotation=(0,1.5707,0),scale=(1, 1, 1))
        
        bpy.data.objects['NurbsPath'].name = str(name)
        return bpy.data.objects[str(name)]
    
    def add_beizer_curve(self, name, location, scale):
        bpy.ops.curve.primitive_bezier_circle_add(enter_editmode=False,
                                                  align='WORLD',
                                                  location=location,
                                                  scale=scale
                                                  )
        bpy.data.objects['BezierCircle'].name = str(name)
        return bpy.data.objects[str(name)]

    def set_random_curve_height(curve_object, min_value, max_value):
        """ This function sets the height of the path curve for randomness/variation
        """
        z_value = round(random.uniform(min_value, max_value), 2)
        bpy.data.objects['camera_track'].location[2] = z_value

    def track_object(self, tracking_object_name, object_to_track):
        """ Function to make camera track the objects
        """
        tracking_object = bpy.data.objects[str(tracking_object_name)]
        if not str('Track To') in tracking_object.constraints.keys():
            tracking_object.constraints.new(type="TRACK_TO")
            tracking_object.constraints['Track To'].target = object_to_track
        else:
            tracking_object.constraints['Track To'].target = object_to_track

    def add_background_plane(self, plane_size, name):
        """
        This function adds the background plane to the scene along with a default material.
        """
        bpy.ops.mesh.primitive_plane_add(
            size=plane_size, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        bpy.data.objects['Plane'].name = name
        return bpy.data.objects[str(name)]

    def add_camera(self, camera_name: str):
        """
        Adds a camera to the origin of the scene 

        Keyword arguments:
        camera_name -- Name for the camera: str 
        """
        bpy.ops.object.camera_add(
            location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
        bpy.context.object.data.lens = 50
        bpy.context.object.data.name = str(camera_name)
        bpy.context.scene.camera = bpy.context.object
        return bpy.data.objects[str(camera_name)]

    def add_light_source(self, type: str, obj_name: str, shadow: bool):
        """
        Adds a light source with respective type to the origin of the scene.

        Keyword arguments:
        type -- The type of light source, default SUN, other: POINT,AREA,SPOT
        obj_name -- Name for the object: str
        shadow -- Enable or Disable shadows: bool

        returns: Light object
        """
        bpy.ops.object.light_add(
            type=str(type).upper(), radius=1, location=(0, 0, 0))
        bpy.context.object.data.name = str(obj_name)
        bpy.context.object.data.energy = 5
        bpy.context.object.data.use_shadow = shadow
        bpy.context.object.data.use_contact_shadow = shadow
        return bpy.data.objects[str(obj_name)]

    def set_camera(self, obj_name: str, position: tuple, rotation: tuple):
        """
        This function sets the camera to the desired location and orientation.
        """
        bpy.data.cameras[str(obj_name)].location = position
        bpy.data.cameras[str(obj_name)].Rotation = rotation

    def set_light_source(self, obj_name: str, position: tuple, rotation: tuple):
        """
        Sets the light source to the desired loacation,orientation and energy values.

        Keyword arguments:
        obj_name -- Name of the light object: str
        position -- Position values of the light object: (float,float,float)
        rotation -- Rotation values of the light object: (float,float,float)
        """
        bpy.data.lights[str(obj_name)].location = position
        bpy.data.lights[str(obj_name)].Rotation = rotation

    def get_object_names(self, background_plane_name, camera_track, light_track):
        """
        returns list of object names present in the scene after removing unnecessary things.

        Keyword arguments:
        background_plane_name--name of the background plane object: str
        """

        obj_names = bpy.context.scene.objects.keys()
        for name in bpy.data.cameras.keys():
            obj_names.remove(name)
        for name in bpy.data.lights.keys():
            obj_names.remove(name)

        obj_names.remove(str(background_plane_name))
        obj_names.remove(str(camera_track))
        obj_names.remove(str(light_track))
        return sorted(obj_names)

    def hide_objects(self, obj_names, hide: bool):
        """
        hides the objects present in the scene during rendering.
        """
        for name in obj_names:
            bpy.context.scene.objects[name].hide_render = hide


    def random_placement(self,obj, camera, min_distance_factor):
        scene = bpy.context.scene
        # Get the current camera field of view in degrees if not provided
    
        fov_radians = camera.data.angle
        print(f"\nFov radians is : {fov_radians} ")
        # Calculate camera height and width for the current FOV
        aspect_ratio = camera.data.sensor_width / camera.data.sensor_height
        aspect_ratio = scene.render.resolution_x/scene.render.resolution_y
        camera_z_loc = camera.matrix_world.decompose()[0][2]
        print(f"Camera Z location is : {camera_z_loc}")
        camera_height = 2 * camera_z_loc * tan(fov_radians / 2)
        camera_width = camera_height * aspect_ratio
        
        # Calculate the size of the object within the camera frame (e.g., 20% of camera width)
        object_size_percentage = 0.1
        object_width = object_size_percentage * camera_width
        
        print(f"Object width is {object_width}")
        # Calculate the maximum distance for the object based on its size and desired size within the frame
        max_distance = object_width / (2 * tan(fov_radians / 2))
        
        # Calculate the minimum distance based on a factor of the maximum distance
        min_distance = min_distance_factor * max_distance
        
        # Calculate random distance within the range
        print(f'Maximum distance is {max_distance}, Minimum distance is : {min_distance}')
        random_distance = random.uniform(min_distance, max_distance)
        
        # Calculate random angle (azimuth) around the camera
        random_angle = random.uniform(0, 2 * np.pi)
        
        # Calculate the object position relative to the camera
        random_x = random_distance * cos(random_angle)
        random_y = random_distance * sin(random_angle)
        random_z = obj.dimensions.z / 2
        
        print(f'Original x is {obj.location.x} : Random x is {random_x} Original y is : {obj.location.y} Random y is {random_y}')
        # Set the object location
        obj.location.x = random_x
        obj.location.y = random_y

    def import_objects_obj_format(self, models_dir, target_object_size, dataset_name):
        """
        adds objects from cad format(.obj format) along with their materials.

        models_dir: path for the models
        target_size: controls the size of the objects
        dataset_name: Name of the dataset, Robocup or YCB
        """

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
        bpy.ops.wm.read_factory_settings()
        self.clear_scene()

        for idx, object_file in enumerate(obj_files):

            if dataset_name == 'robocup':
                obj_name = object_file.split('/')[-1].split('.')[0]
            elif dataset_name == 'ycb':
                obj_name = "".join(object_file.split('/')[-3].split('_')[1::])

            # Import the OBJ file
            bpy.ops.import_scene.obj(filepath=object_file)

            # Set the active object to the imported object
            imported_object = bpy.context.selected_objects[-1]
            # Rename the new object
            imported_object.name = str(obj_name)
            object_names.append(imported_object.name)

            if imported_object is not None:
                # Get the maximum dimension of the object
                max_dimension = max(imported_object.dimensions)

                # Calculate the scale factor to achieve the target size
                scale_factor = target_object_size / max_dimension

                # Apply scale transformation to the object
                imported_object.scale = (
                    scale_factor, scale_factor, scale_factor)

                # Set the origin of the object to its center
                imported_object.select_set(True)
                bpy.context.view_layer.objects.active = imported_object
                bpy.ops.object.origin_set(
                    type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
                imported_object.location = (0.0, 0.0, 0.0)
                imported_object.rotation_euler = (0.0, 0.0, 0.0)
            else:
                print("Error: Object is None")

        return None

    def get_object(self, obj_name):
        """
        Returns the object present in the scene.
        """
        return bpy.context.scene.objects[obj_name]

    def set_random_rotation(self, obj_to_change):
        """
        Applies a random rotation to the given object.

        Keyword arguments:
        obj_to_change: blender object
        """

        random_rotat_values = [
            random.random()*2*math.pi, random.random()*2*math.pi, random.random()*2*math.pi]
        obj_to_change.rotation_euler = Euler(random_rotat_values, 'XYZ')

    def set_random_lighting(self, light_source_name, min_value, max_value):
        """
        Applies random light intensities to the scene.

        Keyword arguments:
        light_source_name:str
        min_value: float
        max_value: float
        """
        # bpy.data.lights[str(light_source_name)].energy = round(random.uniform(min_value,max_value),2)
        bpy.data.lights[str(light_source_name)].energy = random.uniform(
            min_value, max_value)

    def set_random_focal_length(self, camera_name, min_value, max_value):
        value = random.randint(min_value, max_value)
        bpy.data.cameras[str(camera_name)].lens = float(value)

    def set_random_background_color(self, obj_name):
        """Applies Materials randomly to the object, Changes specially the Principled BSDf Base color values for the given object's material.

        Keyword arguments:
        obj_name: str
        """
        material_to_change = bpy.data.objects[str(obj_name)].active_material
        # bpy.data.materials[material_name]
        color = Color()
        hue = random.random()  # Random hue between 0 and 1
        color.hsv = (hue, 0.85, 0.85)
        rgba = [color.r, color.g, color.b, 1]
        material_to_change.node_tree.nodes['Principled BSDF'].inputs[0].default_value = rgba

    def set_render_parameters(self, device, render_engine, res_x, res_y, num_samples):
        """Sets the active scene with the specified render parameters.

        Keyword arguments:
        device-- Type of the device CPU or GPU : str
        res_x-- resolution width of the image to render: int
        res_y-- resolution height of the image to render: int
        num_samples-- number of render samples 
        """
        scene = bpy.context.scene
        scene.render.engine = str(render_engine)
        scene.cycles.device = str(device).upper()
        scene.render.resolution_x = int(res_x)
        scene.render.resolution_y = int(res_y)
        scene.render.resolution_percentage = 100
        scene.cycles.samples = num_samples
        scene.render.image_settings.file_format = "PNG"

    def get_texture_map_paths(self, texture_folder):
        """Returns paths for the images which can be used for image textures.

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

    def get_texture_paths(self, texture_dir):
        """Gets the paths for all the texture_folders from the main textures folder and returns them as a list

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

    def set_random_pbr_img_textures(self, textures_path, obj_name, scale):
        """Applies image textures randomly from the available images to the specified object.

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
        obj = bpy.data.objects[obj_name]

        if obj.data.materials:
            obj.data.materials.append(material)
            obj.active_material = bpy.data.materials[material_name]
        else:
            obj.data.materials.append(material)
            obj.active_material = material

        # print("List of materials : ", bpy.data.materials.keys())

        return material

    def add_blur_dof(self, blur_value,focus_background_name):
        """Adds blur effect to the images using depth of field parameter of the camera.

        Keyword arguments:
        focus_background_name: name of the backgrond plane
        """

        camera = bpy.data.objects['Camera']
        camera.data.dof.use_dof = True
        # camera.data.dof.focus_object = bpy.data.objects[str(focus_background_name)]
        camera.data.dof.focus_distance = blur_value

    def deform_objects(self, obj_to_deform):
        """ Deforms the object using simple deform modifer properties

        Keyword arguments:
            obj_to_deform: blender object to deform
        """

        if not 'simple_deform' in obj_to_deform.modifiers.keys():
            obj_to_deform.modifiers.new(
                name="simple_deform", type='SIMPLE_DEFORM')
            deform_modifier = obj_to_deform.modifiers['simple_deform']
        else:
            deform_modifier = obj_to_deform.modifiers['simple_deform']
        deform_modifier.deform_method = 'BEND'

        deform_modifier.deform_axis = 'Z'
        deform_modifier.angle = random.uniform(-0.523, -3.14)

    def adjust_object_position(self, obj, target_size, background_plane):
        """
        moves the objects above the background plane.

        Keyword arguments:
        obj: blender mesh object
        target_size: gap between the object and the background plane. 
        """
        max_dim = np.max(obj.dimensions)
        lift_distance = (max_dim + target_size) / 2
        obj.location.z = lift_distance

    def track_camera_object(self, object_to_track):
        camera = bpy.data.objects['Camera']
        if not str('Track To') in camera.constraints.keys():
            camera.constraints.new(type="TRACK_TO")
            camera.constraints['Track To'].target = object_to_track

    def track_light_object(self, object_to_track):
        light = bpy.data.objects['Sun']
        if not str('Track To') in light.constraints.keys():
            light.constraints.new(type="TRACK_TO")
            light.constraints['Track To'].target = object_to_track

    def random_camera_position(self, camera_name):
        camera = bpy.data.objects[str(camera_name)]
        camera.constraints['Follow Path'].offset = random.randint(0, 100)

    def random_light_position(self, light_name):
        light = bpy.data.objects[str(light_name)]
        light.constraints['Follow Path'].offset = random.randint(0, 100)

    def reset_obj_location_rotation(self, obj):
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)

    def set_camera_postion_on_path(self,camera_name,distance_value):
        camera = bpy.data.objects[str(camera_name)]
        camera.constraints['Follow Path'].offset = distance_value
