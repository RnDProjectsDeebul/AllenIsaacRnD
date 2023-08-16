#!/usr/bin/env python3

import inspect
import numpy as np
import os
import spatialmath as sm
import sys
import textwrap

from quadricslam import QuadricSlam, visualise
from quadricslam.data_source.BOP_YCB import BOP_YCB_dataset
from quadricslam.detector.from_bbox import FromBbox


from typing import Any, List, Optional, Tuple
from quadricslam.data_associator.quadric_iou_associator import QuadricIouAssociator
from quadricslam.visual_odometry.rgbd_cv2 import RgbdCv2
from quadricslam.utils import initialise_quadric_from_depth, ps_and_qs_from_values

import json
import gtsam
import gtsam_quadrics


    
def run():

    # Confirm dataset path is provided
    if len(sys.argv) != 2:
        print("ERROR: Path to dataset is a required argument.")
        sys.exit(1)
    dataset_path = sys.argv[1]

    # Pull camera calibration parameters.
    # (fx, fy, skew, u0, v0) - (1,5,2,3,6)
    # camera_calib = np.array([517.3, 516.5, 0, 318.6, 255.3])

    # Run QuadricSLAM
    q = QuadricSlam(
        data_source=BOP_YCB_dataset(path=dataset_path),
        detector=FromBbox(path=dataset_path),
        # TODO needs a viable data association approach
        associator=QuadricIouAssociator(),
        optimiser_batch=True,
        quadric_initialiser = initialise_quadric_from_depth,
        noise_odom = np.array([0.0] * 6, dtype=np.float64),
        on_new_estimate=(
            lambda state: visualise(state.system.estimates, state.system.
                                    labels, state.system.optimiser_batch)))
    q.spin()
    # visual_odometry=RgbdCv2()

    # store as json
    # estimated poses and quadric parameters
    poses, quadrics = ps_and_qs_from_values(q.state.system.estimates)

    # label for each quadric key
    labels = q.state.system.labels

    # convert from gtsam.pose3 format to numpy array for the values
    keys = poses.keys()
    for k in keys:
        poses[k] = poses[k].matrix().tolist()

    # 5 usefull functions to convert from ConstrainedDualQuadric to serializable format
    # pose, radii, centroid, matrix, normalizedMatrix - Q / Q(3, 3)
    # https://github.com/qcr/gtsam-quadrics/blob/master/gtsam_quadrics/geometry/ConstrainedDualQuadric.h
    keys = quadrics.keys()
    for k in keys:
        temp = np.eye(4)
        temp[:3, :3] = quadrics[k].pose().rotation().matrix()
        temp[:3, 3] = quadrics[k].pose().translation()
        quadrics[k] = {"pose": temp.tolist(),
                       "centroid": quadrics[k].centroid().tolist(),
                       "radii": quadrics[k].radii().tolist()
                       }

    # save as a dictionary
    dict_list = {"poses": poses, "quadrics": quadrics, "labels": labels}
    

    # dump into JSON file
    with open(dataset_path + "/output.json", "w") as json_file:
        json.dump(dict_list, json_file)

if __name__ == '__main__':
    run()
