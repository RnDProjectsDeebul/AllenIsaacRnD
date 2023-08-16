from itertools import groupby
from types import FunctionType
from typing import Callable, Dict, List, Optional, Union

import gtsam
import gtsam_quadrics
import numpy as np
from spatialmath import SE3

from .data_associator import DataAssociator
from .data_source import DataSource
from .detector import Detector
from .quadricslam_states import QuadricSlamState, StepState, SystemState
from .utils import (
    QuadricInitialiser,
    initialise_quadric_ray_intersection,
    new_factors,
    new_values,
    ps_and_qs_from_values,
)
from .visual_odometry import VisualOdometry
import matplotlib.pyplot as plt


class QuadricSlam:

    def __init__(
        self,
        data_source: DataSource,
        visual_odometry: Optional[VisualOdometry] = None,
        detector: Optional[Detector] = None,
        associator: Optional[DataAssociator] = None,
        initial_pose: Optional[SE3] = None,
        noise_prior: np.ndarray = np.array([0] * 6, dtype=np.float64),
        noise_odom: np.ndarray = np.array([0.01] * 6, dtype=np.float64),
        noise_boxes: np.ndarray = np.array([3] * 4, dtype=np.float64),
        optimiser_batch: Optional[bool] = None,
        optimiser_params: Optional[Union[gtsam.ISAM2Params,
                                         gtsam.LevenbergMarquardtParams,
                                         gtsam.GaussNewtonParams]] = None,
        on_new_estimate: Optional[Callable[[QuadricSlamState], None]] = None,
        quadric_initialiser:
        QuadricInitialiser = initialise_quadric_ray_intersection
    ) -> None:
        # TODO this needs a default data associator, we can't do anything
        # meaningful if this is None...
        if associator is None:
            raise NotImplementedError('No default data associator yet exists, '
                                      'so you must provide one.')
        self.associator = associator
        self.data_source = data_source
        self.detector = detector
        self.visual_odometry = visual_odometry

        self.on_new_estimate = on_new_estimate
        self.quadric_initialiser = quadric_initialiser

        # Bail if optimiser settings and modes aren't compatible
        if (optimiser_batch == True and
                type(optimiser_params) == gtsam.ISAM2Params):
            raise ValueError("ERROR: Can't run batch mode with '%s' params." %
                             type(optimiser_params))
        elif (optimiser_batch == False and optimiser_params is not None and
              type(optimiser_params) != gtsam.ISAM2Params):
            raise ValueError(
                "ERROR: Can't run incremental mode with '%s' params." %
                type(optimiser_params))
        if optimiser_params is None:
            optimiser_params = (gtsam.LevenbergMarquardtParams()
                                if optimiser_batch is True else
                                gtsam.ISAM2Params())

        # Setup the system state, and perform a reset
        self.state = QuadricSlamState(
            SystemState(
                initial_pose=SE3() if initial_pose is None else initial_pose,
                noise_prior=noise_prior,
                noise_odom=noise_odom,
                noise_boxes=noise_boxes,
                optimiser_batch=type(optimiser_params) != gtsam.ISAM2Params,
                optimiser_params=optimiser_params))
        self.reset()

    # the same function is used in both optimising by batch and incrementatl optimisation.
    # so in batch optimisation, the s.estimates is empty till the end and then only all the 
    # values from the factor graph are dumped into the initial estimate and optimised on that
    # - its more accurate as the dround truth odom is untouched till end and also the quadrics may have 
    # multiple views to get a better estimate.
    # in incremental optimisation, we need to check that the pose or the quadric key already has an
    # estimate within the s.estimates. if not, then only an initial estimate is added to it. Less accurate
    # as the ground truth odom may be pushed towards erroneous positions by the unstable quadrics with very few views
    def guess_initial_values(self) -> None:
        # Guessing approach (only guess values that don't already have an
        # estimate):
        # - guess poses using dead reckoning
        # - guess quadrics using Euclidean mean of all observations
        s = self.state.system

        fs = [s.graph.at(i) for i in range(0, s.graph.nrFactors())]

        # Start with prior factors
        for pf in [
                f for f in fs if type(f) == gtsam.PriorFactorPose3 and
                not s.estimates.exists(f.keys()[0])
        ]:
            s.estimates.insert(pf.keys()[0], pf.prior())

        # Add all between factors one-by-one (should never be any remaining,
        # but if they are just dump them at the origin after the main loop)
        bfs = [f for f in fs if type(f) == gtsam.BetweenFactorPose3]
        done = False
        while not done:
            bf = next((f for f in bfs if s.estimates.exists(f.keys()[0]) and
                       not s.estimates.exists(f.keys()[1])), None)
            if bf is None:
                done = True
                continue
            s.estimates.insert(
                bf.keys()[1],
                s.estimates.atPose3(bf.keys()[0]) * bf.measured())
            bfs.remove(bf)
        for bf in [
                f for f in bfs if not all([
                    s.estimates.exists(f.keys()[i])
                    for i in range(0, len(f.keys()))
                ])
        ]:
            s.estimates.insert(bf.keys()[1], gtsam.Pose3())

        # Add all quadric factors
        _ok = lambda x: x.objectKey()
        bbs = sorted([
            f for f in fs if type(f) == gtsam_quadrics.BoundingBoxFactor and
            not s.estimates.exists(f.objectKey())
        ],
                     key=_ok)
        for qbbs in [list(v) for k, v in groupby(bbs, _ok)]:
            self.quadric_initialiser(
                [s.estimates.atPose3(bb.poseKey()) for bb in qbbs],
                [bb.measurement() for bb in qbbs],
                self.state).addToValues(s.estimates, qbbs[0].objectKey())

    def spin(self) -> None:
        while not self.data_source.done():
            self.step()

        if self.state.system.optimiser_batch:
            self.guess_initial_values()
            s = self.state.system
            s.optimiser = s.optimiser_type(s.graph, s.estimates,
                                           s.optimiser_params)
            s.estimates = s.optimiser.optimize()

            if self.on_new_estimate:
                self.on_new_estimate(self.state)

        #pos, quad = ps_and_qs_from_values(self.state.system.estimates)
        # data to be recorded. pos, quad, labels
        # print(self.state.this_step.i)
        # # data to be recorded. pos, quad, labels
        # print(len(pos)) # to check if each image is each pose
        #print(quad) # get the value of dual quadrics
        #print(self.state.system.labels) # to get the label for the quadric id
        #input("wait")

    def step(self) -> None:
        # Setup state for the current step
        s = self.state.system
        p = self.state.prev_step
        n = StepState(
            0 if self.state.prev_step is None else self.state.prev_step.i + 1)
        self.state.this_step = n

        # 0 8646911284551352320
        # print(self.state.this_step.i, self.state.this_step.pose_key)

        # Get latest data from the scene (odom, images, and detections)
        n.odom, n.rgb, n.depth = (self.data_source.next(self.state))
        # print("rgb", n.rgb)
        # print("rgb", n.rgb.shape)
        # print("depth", n.depth)
        # print("depth", n.depth.shape)
        # print("from gt", n.odom)
        # if self.state.this_step.i==2:
        #     raise("testing")
        if self.visual_odometry is not None:
            n.odom = self.visual_odometry.odom(self.state)
            print("from visual", n.odom)
        # example is {tv, [358.126, 1.7884141, 587.1226, 154.95697], None, 8646911284551352386}
        # {label, bounds, quadric key, pose key} - posekey increments by 1 after each iteration
        n.detections = (self.detector.detect(self.state)
                        if self.detector else [])
        # print(n.detections[0].label, n.detections[0].bounds, n.detections[0].quadric_key, n.detections[0].pose_key)
        # if self.state.this_step.i==2:
        #     raise("testing")
        # print(n.detections[0].label, n.detections[0].bounds, n.detections[0].quadric_key, n.detections[0].pose_key)
        n.new_associated, s.associated, s.unassociated = (
            self.associator.associate(self.state))

        # Extract some labels
        # TODO handle cases where different labels used for a single quadric???
        # add the label along with the quadric number used for that.
        s.labels = {
            d.quadric_key: d.label
            for d in s.associated
            if d.quadric_key is not None
        }

       
        # # Add new pose to the factor graph
        if p is None:
            #print(n.odom)
            #print(s.initial_pose)
            #print(s.labels)
            #plt.imshow(n.rgb)
            #plt.show()
            #raise("error")
            #print(type(s.initial_pose))
            # s.initial_pose is gtsam format of R and t and is eye(3) and zeros(3)
            # problem is adding the detections of the first cycle with pose as this initial pose
            # added as gtsam format of R and t from the SE3 format
            #print(gtsam.Pose3(n.odom))
            # s.initial_pose = gtsam.Pose3() # CASE 1 -> START AT ORIGIN
            s.initial_pose = gtsam.Pose3(gtsam.Rot3(n.odom[:3,:3]), gtsam.Point3(n.odom[:3, 3])) # CASE 1 -> START AT ACTUAL POSITION
            # print(s.initial_pose)
            s.graph.add(
                gtsam.PriorFactorPose3(n.pose_key, s.initial_pose,
                                       s.noise_prior))
        else:
            #print(n.odom)
            #print(gtsam.Pose3(((SE3() if p.odom is None else p.odom).inv() *
            #                     (SE3() if n.odom is None else n.odom)).A))
            # the odometry value to be added to the graph is the relative odometry between 
            # previous and current pose

            # T = np.eye(4)
            # T[:3,:3] = n.odom[:3,:3] @ p.odom[:3,:3].T
            # T[:3, 3] = n.odom[:3, 3] - T[:3,:3] @ p.odom[:3, 3]
            # odometry = gtsam.Pose3(gtsam.Rot3(T[:3,:3]), gtsam.Point3(T[:3, 3])) # CASE 2 -> n.odom = np.dot(odometry, p.odom)

            # for printing
            # odometry_numpy = np.eye(4)
            # odometry_numpy[:3, :3] = odometry.rotation().matrix() 
            # odometry_numpy[:3, 3] = odometry.translation()
            # print(self.state.prev_step.i + 1)
            # print(p.odom)
            # print(n.odom)
            # print(np.dot(odometry_numpy, p.odom))

            pose_1 = gtsam.Pose3(gtsam.Rot3(p.odom[:3,:3]), gtsam.Point3(p.odom[:3, 3]))
            pose_2 = gtsam.Pose3(gtsam.Rot3(n.odom[:3,:3]), gtsam.Point3(n.odom[:3, 3]))
            odometry = pose_1.between(pose_2) # CASE 2 -> n.odom = np.dot(p.odom, odometry)

            # for printing
            # odometry_numpy = np.eye(4)
            # odometry_numpy[:3, :3] = odometry.rotation().matrix() 
            # odometry_numpy[:3, 3] = odometry.translation()
            # print(self.state.prev_step.i + 1)
            # print(p.odom)
            # print(n.odom)
            # print(np.dot(p.odom, odometry_numpy))

            s.graph.add(
                gtsam.BetweenFactorPose3(
                    p.pose_key, n.pose_key,
                    gtsam.Pose3(odometry),
                    s.noise_odom))

        # Add any newly associated detections to the factor graph
        for d in n.new_associated:
            if d.quadric_key is None:
                print("WARN: skipping associated detection with "
                      "quadric_key == None")
                continue
            s.graph.add(
                gtsam_quadrics.BoundingBoxFactor(
                    gtsam_quadrics.AlignedBox2(d.bounds),
                    gtsam.Cal3_S2(s.calib_rgb), d.pose_key, d.quadric_key,
                    s.noise_boxes))

        # Optimise if we're in iterative mode
        if not s.optimiser_batch:
            self.guess_initial_values()
            if s.optimiser is None:
                s.optimiser = s.optimiser_type(s.optimiser_params)
            try:
                # pu.db
                s.optimiser.update(
                    new_factors(s.graph, s.optimiser.getFactorsUnsafe()),
                    new_values(s.estimates,
                               s.optimiser.getLinearizationPoint()))
                s.estimates = s.optimiser.calculateEstimate()
            except RuntimeError as e:
                # For handling gtsam::InderminantLinearSystemException:
                #   https://gtsam.org/doxygen/a03816.html
                pass
            if self.on_new_estimate:
                self.on_new_estimate(self.state)

        self.state.prev_step = n

    def reset(self) -> None:
        self.data_source.restart()

        s = self.state.system
        s.associated = []
        s.unassociated = []
        s.labels = {}
        s.graph = gtsam.NonlinearFactorGraph()
        s.estimates = gtsam.Values()
        s.optimiser = (None if s.optimiser_batch else s.optimiser_type(
            s.optimiser_params))

        s.calib_depth = self.data_source.calib_depth()
        s.calib_rgb = self.data_source.calib_rgb()

        self.state.prev_step = None
        self.state.this_step = None
