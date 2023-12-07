Run the Comparative_Evaluation/noisy_bbox_generator/noisy_bbox_generation.ipynb -> to generate the noisy bounding box file scene_gt_info.json. 

Run the Comparative_Evaluation/noisy_bbox_generator/detections_json_file_creation.ipynb -> to generate the bounding box file for the OA-SLAM

----------------------------------------------------------------------------------------------------------------------------------------------------

To run OA-SLAM

./oa-slam ../Vocabulary/ORBvoc.txt /home/allen/Desktop/RnD_Github/AllenIsaacRnD/noisy_bounding_box_experiment/camera_simulator.yaml /home/allen/Desktop/RnD_Github/AllenIsaacRnD/noisy_bounding_box_experiment/noisy_scene/rgb/ /home/allen/Desktop/RnD_Github/AllenIsaacRnD/noisy_bounding_box_experiment/noisy_scene/detections_yolov5.json null points+objects noisy_test_scene

copy the noisy_test_scene folder contents to oa_slam_result

----------------------------------------------------------------------------------------------------------------------------------------------------


To run QuadricSLAM - batch

conda activate quadricslamtest
python3 /home/allen/anaconda3/envs/quadricslamtest/lib/python3.10/site-packages/quadricslam_examples/BOP_YCB_dataset_test.py /home/allen/Desktop/RnD_Github/AllenIsaacRnD/noisy_bounding_box_experiment/noisy_scene True


To run QuadricSLAM - incremental

conda activate quadricslamtest
python3 /home/allen/anaconda3/envs/quadricslamtest/lib/python3.10/site-packages/quadricslam_examples/BOP_YCB_dataset_test.py /home/allen/Desktop/RnD_Github/AllenIsaacRnD/noisy_bounding_box_experiment/noisy_scene False

----------------------------------------------------------------------------------------------------------------------------------------------------
