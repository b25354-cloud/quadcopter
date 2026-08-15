# Autonomous Quadcopter Framework

An open-source, full-stack autonomous aerial navigation framework developed by the **Robotronics Club at IIT Mandi**. Designed specifically for rugged mountain environments, this system integrates high-performance state estimation, trajectory planning, and computer vision onboard standard multirotor platforms.

---

## Key Features

* **Autonomous Navigation:** Real-time 3D path planning using dynamic occupancy grid mapping and trajectory optimization.
* **State Estimation:** Visual-Inertial Odometry (VIO) integrated with extended Kalman filtering (EKF) for GPS-denied environments.
* **Target Detection & Tracking:** Edge-computed YOLOv8 pipeline for object detection, precise landing zone recognition, and visual tracking.
* **Fail-Safe Systems:** Automated Return-to-Launch (RTL), obstacle fallback avoidance, and low-battery management triggers.
* **Simulation Support:** Full Software-In-The-Loop (SITL) environment integrated with Gazebo and PX4.

---

## Hardware Architecture

---

## Software Stack

* **Operating System:** Ubuntu 22.04 LTS / JetPack 5.x
* **Middleware:** ROS 2 (Humble Hawksbill)
* **Flight Stack:** PX4 Autopilot (v1.14+) via `px4_ros_com` and MicroXRCE-DDS
* **Computer Vision:** OpenCV, CUDA, TensorRT
* **Simulation:** Gazebo Garden / Ignition

---

## Getting Started

### Prerequisites

Ensure you have ROS 2 Humble installed on your host or companion computer.

```bash
# Clone the repository
git clone https://github.com/the-robotronics-club/quadcopter
cd quadcopter

# Install dependencies
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### Build

```bash
# Build using colcon (needs to be written after adding code)
colcon build --symlink-install
source install/setup.bash
```

### Running Simulation (SITL)

To launch the PX4 SITL environment with Gazebo and the ROS 2 autonomy node:

```bash
ros2 launch quadcopter_bringup sitl_simulation.launch.py #needs to be written
```

### Hardware Deployment

1. Establish MAVLink communication between PX4 and Jetson over UART/USB (`/dev/ttyTHS1`).
2. Run the bringup package on the companion computer:

```bash
ros2 launch quadcopter_bringup real_robot.launch.py #needs to be written
```

---

## Repository Structure

```text
needs to be written after pushing code
```

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the project repository.
2. Create your Feature Branch (`git checkout -b feature/AwesomeFeature`).
3. Commit your changes (`git commit -m 'Add some AwesomeFeature'`).
4. Push to the branch (`git push origin feature/AwesomeFeature`).
5. Open a Pull Request detailing your changes.



---

## Contact & Acknowledgments

* **Club:** Robotronics Club, IIT Mandi
* **Website:** [robotronics.iitmandi.ac.in](https://robotronics.iitmandi.ac.in)
* **Email:** robotronics@iitmandi.ac.in
