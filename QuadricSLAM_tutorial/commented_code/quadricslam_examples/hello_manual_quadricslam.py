#!/usr/bin/env python3

import gtsam
import gtsam_quadrics
import numpy as np

from quadricslam import visualise

# https://gtsam.org/doxygen/4.0.0/a02619.html - GTSAM documentation
# https://github.com/qcr/gtsam-quadrics/tree/master/gtsam_quadrics/geometry - GTSAM quadrics documentation
def run():
    # Noise models & shortcuts for generating symbols
    # Noise prior is used along with the first added pose key.
    NOISE_PRIOR = gtsam.noiseModel.Diagonal.Sigmas(
        np.array([1e-1] * 6, dtype=np.float64))
    NOISE_ODOM = gtsam.noiseModel.Diagonal.Sigmas(
        np.array([0.01] * 6, dtype=np.float64))
    # noise related to the measured bounding box
    NOISE_BBOX = gtsam.noiseModel.Diagonal.Sigmas(
        np.array([3] * 4, dtype=np.float64))

    # X is used to store the pose. posekey
    X = lambda i: int(gtsam.symbol('x', i))
    # Q is used to store the quadric. quadrickey
    Q = lambda i: int(gtsam.symbol('q', i))

    # Define the ground truth for our dummy scene:
    # - a trajectory of poses tracing a diamond around the origin
    # - each pose faces towards the origin
    # - 2 quadrics around the origin

    # lookat(eye - specifies the camera position, target - the point to look at, upVector-specifies the camera up direction vector.
    # doesn't need to be on the image plane nor orthogonal to the viewing axis, calibration parameters
    poses = [
        gtsam.PinholeCameraCal3_S2.Lookat(x, [0, 0, 0], [0, 0, 1],
                                          gtsam.Cal3_S2()).pose() for x in [
                                              [10, 0, 0],
                                              [0, -10, 0],
                                              [-10, 0, 0],
                                              [0, 10, 0],
                                              [10, 0, 0],
                                          ]
    ]
    # pose - quadric pose (Pose3), radii - quadric radii (Vector3)
    # quadric rotation (Rot3), quadric translation (Point3), quadric radii (Vector3)
    quadrics = [
        gtsam_quadrics.ConstrainedDualQuadric(gtsam.Pose3(), [1, 1, 1]),
        gtsam_quadrics.ConstrainedDualQuadric(
            gtsam.Pose3(gtsam.Rot3(), [1, 1, 1]), [1, 1, 1])
    ]
    # each quadric is represented by a 4x4 symmetric matrix
    # print(poses)
    # print(quadrics)

    # Define our graph with:
    # - a prior factor for starting postion
    # - odometry factors between each pose
    # - a bounding box factor for observing the Quadric at each pose
    graph = gtsam.NonlinearFactorGraph()
    

    # added the first pose with symbol x_0
    graph.add(gtsam.PriorFactorPose3(X(0), poses[0], NOISE_PRIOR))
    
    # each new pose is added with relative to the previous pose
    for i in range(len(poses) - 1):
        graph.add(
            gtsam.BetweenFactorPose3(X(i), X(i + 1),
                                     poses[i].between(poses[i + 1]),
                                     NOISE_ODOM))
        
    # there are 5 factors in graph now.(X0, X0-X1, X1-X2, X2-X3, X3-X4)

    # calibration matrix. (double fx, double fy, double s, double u0, double v0)
    # focal length x, focal length y, skew, px - image center in x, py - image center in y
    cal = gtsam.Cal3_S2(525, 525, 0, 160, 120)


    # for each quadric
    for iq, q in enumerate(quadrics):
        # for each pose
        for ip, p in enumerate(poses):
            # gtsam_quadrics.BoundingBoxFactor(bounding box, calibration, posekey, quadrickey, noise)
            graph.add(
                gtsam_quadrics.BoundingBoxFactor(
                    gtsam_quadrics.QuadricCamera.project(q, p, cal).bounds(),
                    cal, X(ip), Q(iq), NOISE_BBOX))
    # projecting quadrics
    # gtsam_quadrics.QuadricCamera.project(quadric, pose, calibration)

    
    # There are in total 15 factors now.
    # 5 pose key factors from before
    # 5 q0 and posekey factors
    # 5 q1 and posekey factors
    
    # above is the first part where the known poses is used to estimate the parameters of the quadric - in other words, mapping
    # below is the second part where the knowledge of the quadrics before is used to estimate the poses - in other words, localization

    # Start with some rubbish estimates for each of the poses, and use the
    # optimiser to recover the trajectory
    # A values structure is a map from keys to values. It is used to specify the value of a bunch of variables in a factor graph.
    values = gtsam.Values()
    
    for i, p in enumerate(poses):
        # (key, value) pair
        # actual pose is not passed into the dictionary. just some random poses are passed.
        values.insert(X(i), gtsam.Pose3())
    
    for i, q in enumerate(quadrics):
        # values.insert(quadrickey Q(i), reference to the quadric q);
        q.addToValues(values, Q(i))

    
    # (nonlinear factor graph, initial variable assignments)
    r = gtsam.LevenbergMarquardtOptimizer(graph, values).optimize()

    # the poses are predicted by the LMOptimizer 

    # prints the 5 posekeys with correct rotation and translation matrixes and the 2 quadrics
    print(r)
    # visualize function takes in the quadrics matrix and 5 poses and visualise them.
    visualise(r, {Q(i): gtsam.Symbol(Q(i)).string() for i in [0, 1]}, True)


if __name__ == '__main__':
    run()
