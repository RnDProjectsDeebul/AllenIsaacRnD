import numpy as np
import gtsam

pose1 = np.array([[1, 0, 0, 1],
                  [0, 1, 0, 2],
                  [0, 0, 1, 3],
                  [0, 0, 0, 1]])

R = pose1[:3, :3]  # Rotation matrix (3x3)
t = pose1[:3, 3]   # Translation vector (3x1)

# Convert the rotation and translation components to a gtsam.Pose3
pose_from_matrix_1 = gtsam.Pose3(gtsam.Rot3(R), gtsam.Point3(t))

pose2 = np.array([[0, 0, 1, 4],
                  [1, 0, 0, 3],
                  [0, 1, 0, 2],
                  [0, 0, 0, 1]])

R = pose2[:3, :3]  # Rotation matrix (3x3)
t = pose2[:3, 3]   # Translation vector (3x1)

# Convert the rotation and translation components to a gtsam.Pose3
pose_from_matrix_2 = gtsam.Pose3(gtsam.Rot3(R), gtsam.Point3(t))

transfer = pose_from_matrix_1.between(pose_from_matrix_2)
print(transfer)

# Extract rotation and translation components
R = transfer.rotation().matrix()     # 3x3 rotation matrix
t = transfer.translation()  # 3x1 translation vector

# Construct the 4x4 transformation matrix
T = np.eye(4)
T[:3, :3] = R
T[:3, 3] = t

print(T)

print(np.dot(pose1, T))