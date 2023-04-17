import gtsam
import gtsam.utils.plot as gtsam_plot
import numpy as np
import matplotlib.pyplot as plt

def run():
    # Create an empty nonlinear factor graph
    graph = gtsam.NonlinearFactorGraph()

    # Create keys for variables
    i1 = gtsam.symbol('x',1)
    i2 = gtsam.symbol('x',2)
    i3 = gtsam.symbol('x',3)
    j1 = gtsam.symbol('l',1)
    j2 = gtsam.symbol('l',2)

    # Add a Gaussian prior on pose x_1
    # prior at origin
    priorMean = gtsam.Pose2(0.0, 0.0, 0.0)
    priorNoise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.3, 0.3, 0.1], dtype=np.float64))
    graph.add(gtsam.PriorFactorPose2(i1, priorMean, priorNoise))

    # Add two odometry factors
    odometry = gtsam.Pose2(2.0, 0.0, 0.0)
    odometryNoise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.2, 0.2, 0.1], dtype=np.float64))

    graph.add(gtsam.BetweenFactorPose2(i1, i2, odometry, odometryNoise))
    graph.add(gtsam.BetweenFactorPose2(i2, i3, odometry, odometryNoise))

    # Add bearing/range measurement factors
    degrees = np.pi/180
    brNoise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.1, 0.2], dtype=np.float64))
    graph.add(gtsam.BearingRangeFactor2D(i1, j1, gtsam.Rot2(45*degrees), np.sqrt(8), brNoise))
    graph.add(gtsam.BearingRangeFactor2D(i2, j1, gtsam.Rot2(90*degrees), 2, brNoise))
    graph.add(gtsam.BearingRangeFactor2D(i3, j2, gtsam.Rot2(90*degrees), 2, brNoise))

    # create (deliberately inaccurate) initial estimate
    initial = gtsam.Values()
    initial.insert(i1, gtsam.Pose2(0.5, 0.0, 0.2))
    initial.insert(i2, gtsam.Pose2(2.3, 0.1, -0.2))
    initial.insert(i3, gtsam.Pose2(4.1, 0.1, 0.1))
    initial.insert(j1, gtsam.Point2(1, 1))
    initial.insert(j2, gtsam.Point2(2, 2))

    # optimize using Levenberg-Marquardt optimization
    result = gtsam.LevenbergMarquardtOptimizer(graph, initial).optimize()

    # print(result)
    
    # query the marginals
    marginals = gtsam.Marginals(graph, result)

    # print("i1 covariance:\n", marginals.marginalCovariance(i1))


    fig = plt.figure(0)
    axes = fig.gca()
    plt.cla()
    axes.set_xlim(-2, 10)
    axes.set_ylim(-5, 5)


    gtsam_plot.plot_pose2(0, result.atPose2(i1), 5, marginals.marginalCovariance(i1))
    plt.pause(1)
    gtsam_plot.plot_pose2(0, result.atPose2(i2), 5, marginals.marginalCovariance(i2))
    plt.pause(1)
    gtsam_plot.plot_pose2(0, result.atPose2(i3), 5, marginals.marginalCovariance(i3))
    plt.pause(1)
    gtsam_plot.plot_point2(0, result.atPoint2(j1), 5, marginals.marginalCovariance(j1))
    plt.pause(1)
    gtsam_plot.plot_point2(0, result.atPoint2(j2), 5, marginals.marginalCovariance(j2))
    plt.pause(1)
    axes.plot([result.atPoint2(j1)[0], result.atPose2(i1).translation()[0]],
              [result.atPoint2(j1)[1], result.atPose2(i1).translation()[1]], color = 'b', linestyle='dashed')
    axes.plot([result.atPoint2(j1)[0], result.atPose2(i2).translation()[0]],
              [result.atPoint2(j1)[1], result.atPose2(i2).translation()[1]], color = 'b', linestyle='dashed')
    axes.plot([result.atPoint2(j2)[0], result.atPose2(i3).translation()[0]],
              [result.atPoint2(j2)[1], result.atPose2(i3).translation()[1]], color = 'b', linestyle='dashed')
    plt.pause(1)


    plt.ioff()
    plt.show()


if __name__ == '__main__':
    run()