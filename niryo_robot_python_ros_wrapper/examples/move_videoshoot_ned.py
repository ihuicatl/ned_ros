#!/usr/bin/env python

# To use the API, copy these 4 lines on each Python file you create
from niryo_robot_python_ros_wrapper.ros_wrapper import *
import rospy
import time
import math

WHITE = [255, 255, 255]
GREEN = [50, 255, 0]
BLACK = [0, 0, 0]
BLUE = [15, 50, 255]
PURPLE = [153, 51, 153]
PINK = [255, 0, 255]
RED = [255, 0, 0]
CYAN = [0, 255, 255]

rospy.init_node('niryo_robot_example_python_ros_wrapper')

print "--- Start"

n = NiryoRosWrapper()
# n.request_new_calibration()
n.set_arm_max_velocity(100)
n.calibrate_auto()

print "--- Prepare traj --"

n.move_joints(*(6 * [0]))
n.move_pose(*[0.029, 0.217, 0.3, 2.254, 1.476, -2.38])
print ("-- Compute traj 1 --")
traj1 = n.compute_trajectory_from_poses_and_joints(
    [[0.029, 0.217, 0.3, 2.254, 1.476, -2.38], [0.029, 0.217, 0.15, 2.254, 1.476, -2.38],
     [0.03, 0.217, 0.3, 2.254, 1.476, -2.38], [0.159, 0.126, 0.3, 0.062, 1.535, 0.96],
     [0.159, 0.126, 0.15, 0.062, 1.535, 0.96], [0.16, 0.126, 0.3, 0.062, 1.535, 0.96],
     [0.219, -0.019, 0.3, -1.555, 1.544, -1.526], [0.219, -0.019, 0.15, -1.555, 1.544, -1.526],
     [0.22, -0.019, 0.3, -1.555, 1.544, -1.526], [0.16, -0.175, 0.3, -2.693, 1.529, 2.976],
     [0.16, -0.175, 0.15, -2.693, 1.529, 2.976], [0.17, -0.175, 0.3, -2.693, 1.529, 2.976],
     [-0.015, -0.229, 0.3, -2.552, 1.563, 2.298], [-0.015, -0.229, 0.15, -2.552, 1.563, 2.298],
     [-0.016, -0.229, 0.3, -2.552, 1.563, 2.298]],
    ["pose", "pose", "pose", "pose", "pose", "pose", "pose", "pose", "pose", "pose", "pose", "pose", "pose", "pose",
     "pose"], 0.01)
# n.execute_moveit_robot_trajectory(traj1)

print ("-- Compute traj 4 --")
pose_list = [
    [0.3, -0.16, 0.325, 0, 0, 0],
    [0.3, -0.13, 0.32, 0, 0, 0],
    [0.3, -0.09, 0.30, 0, 0, 0],
    [0.3, -0.06, 0.26, 0, 0, 0],
    [0.3, -0.03, 0.21, 0, 0, 0],
    [0.3, 0, 0.2, 0, 0, 0],
    [0.3, 0.03, 0.21, 0, 0, 0],
    [0.3, 0.06, 0.26, 0, 0, 0],
    [0.3, 0.09, 0.30, 0, 0, 0],
    [0.3, 0.13, 0.32, 0, 0, 0],
    [0.3, 0.16, 0.325, 0, 0, 0],
]
full_traj = pose_list[:]
pose_list.reverse()
pose_list[-1][1] += 0.01
full_traj += pose_list[:]

n.move_pose(*full_traj[0])
niryo_wave_traj = n.compute_trajectory_from_poses(full_traj, 0.001)
# n.execute_moveit_robot_trajectory(niryo_wave_traj)


# Slalome
print ("-- Compute traj 5 --")
start_pose = [0.2, -0.2, 0.15, 0, 1.57, 0]
pose_list = [start_pose]
for _ in range(2):
    new_pose = pose_list[-1][:]
    new_pose[0] += 0.1
    pose_list.append(new_pose[:])
    new_pose[1] += 0.1
    pose_list.append(new_pose[:])
    new_pose[0] -= 0.1
    pose_list.append(new_pose[:])
    new_pose[1] += 0.1
    pose_list.append(new_pose[:])
for _ in range(2):
    new_pose = pose_list[-1][:]
    new_pose[0] += 0.1
    pose_list.append(new_pose[:])
    new_pose[1] -= 0.1
    pose_list.append(new_pose[:])
    new_pose[0] -= 0.1
    pose_list.append(new_pose[:])
    new_pose[1] -= 0.1
    pose_list.append(new_pose[:])

n.move_pose(*pose_list[0])
slalome_traj = n.compute_trajectory_from_poses(pose_list, 0.001)
# n.execute_moveit_robot_trajectory(slalome_traj)

print("-- Go --")

while True:
    try:
        # Calibrate robot first
        # n.request_new_calibration()
        n.wait(0.1)
        n.calibrate_auto()
        n.update_tool()
        n.grasp_with_tool()
        print "Calibration finished !"

        print("Wave")
        n.move_joints(*(6 * [0]))
        # Niryo wave
        n.move_pose(*full_traj[0])
        n.set_arm_max_velocity(50)
        n.execute_moveit_robot_trajectory(niryo_wave_traj)
        n.wait(0.5)
        n.set_arm_max_velocity(100)

        print("Moves")
        n.move_pose(*[0.094, -0.085, 0.3, 0.927, 1.157, 0.899])
        n.move_pose(*[0.029, 0.217, 0.3, 2.254, 1.476, -2.38])
        n.execute_moveit_robot_trajectory(traj1)
        n.move_pose(*[0.179, 0.001, 0.264, 2.532, 1.532, 2.618])

        print("Spiral")
        n.move_pose(0.3, 0, 0.3, 0, 0, 0)
        n.move_spiral(0.1, 5, 216, 1)

        print("Circle")
        n.move_pose(0.3, 0, 0.4, 0, 0, 0)
        n.move_circle(0.3, 0, 0.3)

        print("Linear")
        n.move_pose(0.2, 0.2, 0.2, 0, 1.57, 0)
        n.move_linear_pose(0.2, -0.2, 0.2, 0, 1.57, 0)

        # Slalome
        print("Slalome")
        n.move_pose(*pose_list[0])
        n.execute_moveit_robot_trajectory(slalome_traj)

        print("Pick and place")
        pick_1 = [
            [0.25, -0.15, 0.25, 0, 1.57, 0],
            [0.25, -0.15, 0.145, 0, 1.57, 0],
        ]
        place_1 = [
            [0.25, -0.15, 0.35, 0, 1.57, 0],
            [0.25, 0.05, 0.35, 0, 1.57, 0],
            [0.25, 0.05, 0.2, 0, 1.57, 0],
        ]

        pick_2 = [
            [0.25, 0.05, 0.25, 0, 1.57, 0],
            [0.25, 0.15, 0.25, 0, 1.57, 0],
            [0.25, 0.15, 0.145, 0, 1.57, 0],
        ]
        place_2 = [
            [0.25, 0.15, 0.35, 0, 1.57, 0],
            [0.25, -0.05, 0.35, 0, 1.57, 0],
            [0.25, -0.05, 0.2, 0, 1.57, 0],
        ]

        end_pose = [
            [0.25, -0.05, 0.25, 0, 1.57, 0],
            [0.2, 0, 0.3, 0, 1.57, 0],
        ]

        n.release_with_tool()
        n.execute_trajectory_from_poses(pick_1, 0.002)
        try:
            n.close_gripper(max_torque_percentage=100, hold_torque_percentage=100)
        except Exception:
            pass
        n.execute_trajectory_from_poses(place_1, 0.002)
        n.release_with_tool()
        n.execute_trajectory_from_poses(pick_2, 0.002)
        try:
            n.close_gripper(max_torque_percentage=100, hold_torque_percentage=100)
        except Exception:
            pass
        n.execute_trajectory_from_poses(place_2, 0.002)
        n.execute_trajectory_from_poses(end_pose, 0.002)

        print("Wave")
        n.move_joints(*(6 * [0]))
        # Niryo wave
        n.move_pose(*full_traj[0])
        n.set_arm_max_velocity(50)
        n.execute_moveit_robot_trajectory(niryo_wave_traj)

        n.wait(0.5)
        n.set_arm_max_velocity(100)

    except NiryoRosWrapperException as e:
        print e
        # handle exception here
        # you can also make a try/except for each command separately

print "--- End"
