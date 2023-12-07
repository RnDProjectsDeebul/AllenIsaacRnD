To run the mapping
-------------------------------------------------------------
Changing the rgb.txt files controls how much you map

./oa-slam ../Vocabulary/ORBvoc.txt /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/camera_simulator.yaml /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/rgb/ /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/detections_yolov5.json null points+objects localization_test_scene

after running the map, copy the files to map_full or map_half

----------------------------------------------------------------
To run the localization
----------------------------------------------------------------

./oa-slam_localization ../Vocabulary/ORBvoc.txt /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/camera_simulator.yaml /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/rgb/  /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/detections_yolov5.json null /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/map_full/map_localization_test_scene.yaml points reloc_output 0

./oa-slam_localization ../Vocabulary/ORBvoc.txt /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/camera_simulator.yaml /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/rgb/  /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/detections_yolov5.json null /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/map_full/map_localization_test_scene.yaml points+objects reloc_output 0

./oa-slam_localization ../Vocabulary/ORBvoc.txt /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/camera_simulator.yaml /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/rgb/  /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/detections_yolov5.json null /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/map_half/map_localization_test_scene.yaml points reloc_output 0

./oa-slam_localization ../Vocabulary/ORBvoc.txt /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/camera_simulator.yaml /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/rgb/  /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/detections_yolov5.json null /home/allen/Desktop/RnD_Github/AllenIsaacRnD/localization/test_scene/map_half/map_localization_test_scene.yaml points+objects reloc_output 0

----------------------------------------------------------------

The keyframes for testing
001047.png
001055.png
001071.png -> i have selected

------------------------------------------------------------------

850 to 1200 -> i tested with points only on half map. didnt worked. i tested with points+objects and was able to localize almost precisely.
