from typing import List

from ..quadricslam_states import Detection, QuadricSlamState
from . import Detector
import os
import json


class FromBbox(Detector):

    def __init__(self, path: str) -> None:
        self.path = path

        if not os.path.isdir(self.path):
            raise ValueError("Path '%s' does not exist." % self.path)
        
        img_id = os.listdir(self.path + '/rgb')
        img_id = [os.path.splitext(x)[0] for x in img_id]
        img_id.sort()
        img_id = [str(int(x)) for x in img_id]
        # stores the image id in string format after removing the zeros in beginning
        
        # contains label name of all the label ids
        # self.classes = []
        # to store the predicted class ids as list for each detection
        self.pred_classes_dataset = []
        # to store the predicted class bounding box as list for each detection
        self.pred_boxes_dataset = []

        f1 = open(self.path + '/scene_gt_info.json')
        data1 = json.load(f1)
        f2 = open(self.path + '/scene_gt.json')
        data2 = json.load(f2)

        # loading the dataset for object id and bounding box into list
        for id in img_id:
            temp1 = []
            temp2 = []
            for det in range(len(data1[id])):
                # (x, y, width, height) - in this format to (x, y, x+width, y+height)
                # # https://detectron2.readthedocs.io/en/latest/modules/structures.html#detectron2.structures.Boxes (x1, y1, x2, y2) for detectron
                temp = data1[id][det]['bbox_obj']
                temp[2]+=temp[0]
                temp[3]+=temp[1]
                temp1.append(temp)
                temp2.append(data2[id][det]['obj_id'])
            self.pred_boxes_dataset.append(temp1)
            self.pred_classes_dataset.append(temp2)
        

    def detect(self, state: QuadricSlamState) -> List[Detection]:
        assert state.this_step is not None
        assert state.this_step.rgb is not None
        n = state.this_step

        # contains ids of the predicted detections
        pred_classes = self.pred_classes_dataset[n.i]
        # contains a list of 4 bounds for each detected id
        pred_boxes = self.pred_boxes_dataset[n.i]
        # for i in range(0, len(pred_classes)):
        #     print([pred_classes[i], pred_boxes[i], n.pose_key])
        # raise("error")
        return [
            Detection(label=pred_classes[i],
                      bounds=pred_boxes[i],
                      pose_key=n.pose_key)
            for i in range(0, len(pred_classes))
        ]
