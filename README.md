# AllenIsaacRnD

![Primary language](https://img.shields.io/github/languages/top/RnDProjectsDeebul/AllenIsaacRnD)
[![License](https://img.shields.io/github/license/RnDProjectsDeebul/AllenIsaacRnD)](./LICENSE)

# Semantic Mapping for Enhanced Localization in Indoor Environments

SLAM is employed to construct an environmental map, incorporating both spatial and semantic data from sensors to facilitate later relocalization. Traditional dense mapping techniques proved impractical for resource-limited mobile robots due to computational and storage constraints, necessitating the use of coarse object models to incorporate semantics into the map. Among these, [**QuadricSLAM**](https://github.com/qcr/quadricslam/tree/master) and [**OA-SLAM**](https://gitlab.inria.fr/tangram/oa-slam) are two notable approaches, with the former requiring an RGBD image as input and the latter using an RGB image. Nevertheless, neither of these methods has been assessed on a common dataset to date. To address this gap, a synthetic dataset was generated, allowing for a quantitative assessment of mapping accuracy using various predefined metrics. The results demonstrate OA-SLAM's accuracy and robustness in the face of sensor noise and its capacity to relocalize with a single RGB image of the scene.


## Proposed approach

* The image below shows a sample RGB image of the synthetic scene generated using blender. 5 YCB objects are placed in a scene and the camera moves around this scene. The background texture can also be changed for each scene generated.

<p align="center">
  <img 
    src="readme_images/sample_scene.png"
  >
</p>

* The ground truth trajectory of the camera and object's position in a scene are plotted using matplotlib. The object's ground truth is represented using a cuboid.

<p align="center">
  <img 
    src="readme_images/ground_truth.png"
  >
</p>

* The estimated camera trajectory is compared to the ground truth(left image) and the estimated object pose is compared to the ground truth(right image) based on certain metrics. The estimated object is plotted as an ellipsoid.

| ![Image 1](readme_images/est_traj.png) | ![Image 2](readme_images/est_obj.png) |
| :---------------------: | :---------------------: |



## Usage

* **Text**
