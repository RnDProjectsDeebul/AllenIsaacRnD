from spatialmath import SE3, UnitQuaternion, SO3
from typing import Optional, Tuple
import gtsam
import numpy as np
import os
import cv2

from ..quadricslam_states import QuadricSlamState
from . import DataSource
import json


class BOP_YCB_dataset(DataSource):

    def __init__(self, path:str) -> None:
        # Validate path exists
        self.path = path
        if not os.path.isdir(self.path):
            raise ValueError("Path '%s' does not exist." % self.path)
        
        
        img_id = os.listdir(self.path + '/rgb')
        img_id = [os.path.splitext(x)[0] for x in img_id]
        img_id.sort()
        self.img_id = [str(int(x)) for x in img_id]
        # stores the image id in string format after removing the zeros in beginning

        # load odom
        f1 = open(self.path + '/scene_camera.json')
        data1 = json.load(f1)

        self.odom_data = list(dict())
        for id in self.img_id:
            temp = dict()
            temp['cam_R_w2c'] = data1[id]['cam_R_w2c']
            temp['cam_t_w2c'] = data1[id]['cam_t_w2c']
            temp['cam_K'] = data1[id]['cam_K']
            self.odom_data.append(temp)

        self.data_length = len(self.img_id)
        self.restart()


    # to do. correct calibration parameters
    def calib_rgb(self) -> np.ndarray:
        # Vector representing the calibration (fx, fy, skew, u0, v0)
        # (fx, fy, skew, u0, v0) - (1,5,2,3,6)
        # return np.array([1, 1, 0, 0, 0])
        return [self.odom_data[self.data_i]['cam_K'][0],
                self.odom_data[self.data_i]['cam_K'][4],
                self.odom_data[self.data_i]['cam_K'][1],
                self.odom_data[self.data_i]['cam_K'][2],
                self.odom_data[self.data_i]['cam_K'][5]]


    def done(self) -> bool:
        return self.data_i == self.data_length

    # to do. correct odom
    def _gt_to_SE3(self, i: int) -> SE3:
        # return SE3.Rt(SO3(np.array(self.odom_data[i]['cam_R_w2c']).reshape((3,3))), self.odom_data[i]['cam_t_w2c'])
        mat = np.hstack((np.array(self.odom_data[i]['cam_R_w2c']).reshape((3,3)), np.array(self.odom_data[i]['cam_t_w2c'])[np.newaxis].T))
        mat = np.vstack((mat, np.array([0, 0, 0, 1])))
        # also try to create a random SE3 and then assign value individually
        return mat
    
    # to do. load depth and rgb image and odom
    def next(
        self, state: QuadricSlamState
    ) -> Tuple[Optional[SE3], Optional[np.ndarray], Optional[np.ndarray]]:
        # Tuple is (odom, RGB, depth)
        i = self.data_i
        self.data_i += 1
        return (SE3() if i == 0 else self._gt_to_SE3(i) *
                np.linalg.inv(self._gt_to_SE3(i - 1)),
                cv2.imread(self.path + '/rgb/' + f'{int(self.img_id[i]):06d}' + '.png'),
                cv2.imread(self.path + '/depth/' + f'{int(self.img_id[i]):06d}' + '.png', -1))

    def restart(self) -> None:
        self.data_i = 0
