# ReadMe for saving the results

### Important notes for the output path.
In the argument files if you do not provide any specific output path then the rendered datasets will be directly stored in this results folder with the name of corresponding test_case.

Example: 
  * ycb_normal_training
  * ycb_distance
  * robocup_lighting
  * robocup_blur
  * etc.

If you are generating both classification and regression datasets please create separate folders and provide the output path in the json file to avoid the naming conflict.
Example: 
  * complete_path/results/classification/
  * complete_path/results/regression/
