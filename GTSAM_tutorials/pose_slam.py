import gtsam
import gtsam.utils.plot as gtsam_plot
import numpy as np
import matplotlib.pyplot as plt

def run():
    # Create an empty nonlinear factor graph
    graph = gtsam.NonlinearFactorGraph()

    # Add a Gaussian prior on pose x_1
    priorNoise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.3, 0.3, 0.1], dtype=np.float64))
    graph.add(gtsam.PriorFactorPose2(1, gtsam.Pose2(0.0, 0.0, 0.0), priorNoise))

    # Add two odometry factors
    odometryNoise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.2, 0.2, 0.1], dtype=np.float64))

    graph.add(gtsam.BetweenFactorPose2(1, 2, gtsam.Pose2(2.0, 0.0, 0.0), odometryNoise))
    graph.add(gtsam.BetweenFactorPose2(2, 3, gtsam.Pose2(2.0, 0.0, np.pi/2), odometryNoise))
    graph.add(gtsam.BetweenFactorPose2(3, 4, gtsam.Pose2(2.0, 0.0, np.pi/2), odometryNoise))
    graph.add(gtsam.BetweenFactorPose2(4, 5, gtsam.Pose2(2.0, 0.0, np.pi/2), odometryNoise))

    # loop closure constraint
    graph.add(gtsam.BetweenFactorPose2(5, 2, gtsam.Pose2(2, 0, np.pi/2), odometryNoise))

    # create (deliberately inaccurate) initial estimate
    initial = gtsam.Values()
    initial.insert(1, gtsam.Pose2(0.5, 0.0, 0.2))
    initial.insert(2, gtsam.Pose2(2.3, 0.1, -0.2))
    initial.insert(3, gtsam.Pose2(4.1, 0.1, np.pi/2))
    initial.insert(4, gtsam.Pose2(4.0, 2.0, np.pi/2))
    initial.insert(5, gtsam.Pose2(2.1, 2.1, -np.pi/2))

    # optimize using Levenberg-Marquardt optimization
    result = gtsam.LevenbergMarquardtOptimizer(graph, initial).optimize()

    print(result)
    
    # query the marginals
    marginals = gtsam.Marginals(graph, result)

    print("x1 covariance:\n", marginals.marginalCovariance(1))
    print("x2 covariance:\n", marginals.marginalCovariance(2))
    print("x3 covariance:\n", marginals.marginalCovariance(3))
    print("x4 covariance:\n", marginals.marginalCovariance(4))
    # 5th one will have lower covariance or uncertainty because of loop closure
    print("x5 covariance:\n", marginals.marginalCovariance(5))

    fig = plt.figure(0)
    axes = fig.gca()
    plt.cla()
    axes.set_xlim(-2, 10)
    axes.set_ylim(-5, 5)
    for i in range(1,6):
        gtsam_plot.plot_pose2(0, result.atPose2(i), 5, marginals.marginalCovariance(i))
        plt.pause(1)
    plt.ioff()
    plt.show()


if __name__ == '__main__':
    run()