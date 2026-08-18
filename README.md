# Autonomous Quadcopter Framework

An open-source, full-stack autonomous aerial navigation framework developed by the **Robotronics Club at IIT Mandi**. Designed specifically for rugged mountain environments, this system integrates high-performance state estimation, trajectory planning, and computer vision onboard standard multirotor platforms.

![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-22314E?style=flat-square&logo=ros&logoColor=white)
![PX4](https://img.shields.io/badge/PX4-v1.14+-8A2BE2?style=flat-square)
![NVIDIA Jetson](https://img.shields.io/badge/NVIDIA-Jetson-76B900?style=flat-square&logo=nvidia&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04_LTS-E95420?style=flat-square&logo=ubuntu&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-11.4-76B900?style=flat-square)
![TensorRT](https://img.shields.io/badge/TensorRT-8.x-76B900?style=flat-square)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-00CFFF?style=flat-square)
![Gazebo](https://img.shields.io/badge/Gazebo-Garden-15C46B?style=flat-square)
![Git](https://img.shields.io/badge/Git-Friendly-F05032?style=flat-square&logo=git&logoColor=white)

---

## Key Features

* **Autonomous Navigation:** Real-time 3D path planning using dynamic occupancy grid mapping and trajectory optimization.
* **State Estimation:** Visual-Inertial Odometry (VIO) integrated with extended Kalman filtering (EKF) for GPS-denied environments.
* **Target Detection & Tracking:** Edge-computed YOLOv8 pipeline for object detection, precise landing zone recognition, and visual tracking.
* **Fail-Safe Systems:** Automated Return-to-Launch (RTL), obstacle fallback avoidance, and low-battery management triggers.
* **Simulation Support:** Full Software-In-The-Loop (SITL) environment integrated with Gazebo and PX4.

---

## Hardware Architecture

The platform is built on a **Holybro X500 V2** 500 mm carbon-fiber airframe
with a Pixhawk 6C flight controller (PX4) and an NVIDIA Jetson companion
computer running the ROS 2 autonomy stack.

| Doc | Contents |
| --- | -------- |
| [Hardware](hardware/README.md) | Frame, propulsion, layout, mechanical specs |
| [Electronics](electronics/README.md) | System architecture & data flow |
| [Bill of Materials](electronics/bom.md) | Full parts list |
| [Wiring](electronics/wiring.md) | Connections, motor order, checklist |

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
