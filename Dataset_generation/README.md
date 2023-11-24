# constraint_based_dataset_generator

https://github.com/RnDProjectsDeebul/SathwikPanchangamRnD

Blender based dataset generation using setting some fixed constraint and randomized other settings.


## Usage

1. Add the background texture to appear in the scene in the folder ```./blender_files/constraint_textures/```.
2. Run the script ```./download_ycb_models.py``` to download the required YCB models into the path ```./blender_files/models/ycb_models/```.
3. Copy the necessary models to be appearing in the scene into the ```./blender_files/models/sample_models/``` folder.
4. Edit the file ```./src/object_detection_bop.py``` to change the configuration parameters for the scene.

    * `SAVE_DIR` parameter can be changed to name the ouput folder.
    * `NUM_OF_IMAGES` can be used to control the total number of images created for a scene.
    * ``detection_helper.set_render_parameters(device='GPU',
                                           render_engine='CYCLES',
                                           res_x=640,
                                           res_y=480,
                                           num_samples=100
                                           )`` - the res_x and res_y parameters can be changed to control the resolution of the generated image.
    * `detection_helper.place_objects_randomly(radius=0.17)` - the radius parameter can be changed to control the radius of circle on which the objects are placed equidistant.
    * `detection_helper.set_random_pbr_img_textures(textures_path=TEXTURES_DIR,obj_name=detection_helper.background_plane_name,scale=3.0)` - the scale parameter can be changed to control the scaling of the bacground image used.
    * `circle_points = detection_helper.get_circle_points(radius=1.2,location=[0.0,0.0,0.3],num_points=NUM_OF_IMAGES)` - the radius of the circle along which the camera moves, the location of camera(x,y,z) can be changed here. Only the Z value or the height of the camera is varied.
