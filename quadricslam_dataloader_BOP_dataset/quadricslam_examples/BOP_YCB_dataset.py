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
from quadricslam.utils import initialise_quadric_from_depth

    
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
        optimiser_batch=False,
        quadric_initialiser = initialise_quadric_from_depth,
        visual_odometry=RgbdCv2(),
        on_new_estimate=(
            lambda state: visualise(state.system.estimates, state.system.
                                    labels, state.system.optimiser_batch)))
    q.spin()
    # visual_odometry=RgbdCv2()

if __name__ == '__main__':
    run()
