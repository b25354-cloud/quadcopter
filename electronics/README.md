# Electronics Architecture

The electronics stack is split into five subsystems around the **Pixhawk 6C**
flight controller (PX4) and an **NVIDIA Jetson** companion computer (ROS 2):

![Pixhawk](https://img.shields.io/badge/Pixhawk-6C-8A2BE2?style=flat-square)
![PX4](https://img.shields.io/badge/PX4-v1.14+-8A2BE2?style=flat-square)
![ROS 2](https://img.shields.io/badge/ROS_2-Humble-22314E?style=flat-square&logo=ros&logoColor=white)
![NVIDIA Jetson](https://img.shields.io/badge/NVIDIA-Jetson-76B900?style=flat-square&logo=nvidia&logoColor=white)
![MAVLink](https://img.shields.io/badge/MAVLink-2-1479D1?style=flat-square)
![RealSense](https://img.shields.io/badge/Intel_RealSense-D435i-B5422B?style=flat-square)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-00CFFF?style=flat-square)
![SiK Radio](https://img.shields.io/badge/SiK-433_915_MHz-009739?style=flat-square)
![QGroundControl](https://img.shields.io/badge/QGroundControl-Setup-64C61E?style=flat-square)

```
                        +----------------------+
                        |   RC Controller      |
                        | (RadioMaster TX16S)  |
                        +----------+-----------+
                                   | 2.4 GHz ELRS/SBUS
                                   v
   +-----------+   +---------------+-----------+
   |  Power    |   |   Pixhawk 6C  | RC Rx (R81)|
   |  4S LiPo  |   |  (PX4 v1.14+) |            |
   +-----+-----+   +---+------+----+----+-------+
         |             |      |         |
         v             |      v         v
   +-----+-----+       |  +--------+  +------------+
   |  PM02 V3  |       |  | M10 GPS|  | SiK Telemetry
   | Power Mod |       |  +--------+  | 433/915 MHz |
   +-----+-----+       |              +------+------+
         |             |                     | UART (MAVLink)
         v             |                     v
   +-----+-----+       |              +------------+
   |  PDB XT60 |       |              | Ground     |
   +-----+-----+       |              | Station    |
         |             |              +------------+
         +-----+-------+  FMU PWM OUT
         |             |
    +----+----+   +----+----+
    | ESCs x4 |   | Motors x4|
    | BLHeli  |   | 2216     |
    |  20A    |   | KV920    |
    +---------+   +----------+

   Companion Computer (Jetson Orin Nano)
   -------------------------------------
   | UART ttyTHS1 <--> Pixhawk TELEM2 (MAVLink/µXRCE-DDS)
   | USB3 <--> RealSense D435i (VIO + depth)
   | CSI/USB <--> RGB camera (YOLOv8 detection)
   | Ethernet/WiFi <--> Ground Station (ROS 2 bridge)
```

---

## Subsystem Overview

### 1. Flight Control (PX4)
- **Pixhawk 6C** running PX4 v1.14+.
- Runs attitude/velocity control, failsafes, RTL, and actuator output.
- Speaks MAVLink over UART; also runs µXRCE-DDS for direct ROS 2 topics.

### 2. Companion Computer (ROS 2)
- **NVIDIA Jetson Orin Nano (8 GB)** running Ubuntu 22.04 / JetPack 5.x.
- Hosts the autonomy stack: VIO fusion, occupancy grid, trajectory planning,
  YOLOv8 detection/tracking, and the MAVLink ↔ ROS 2 bridge.
- Linked to the Pixhawk via UART `ttyTHS1` (or USB) as the second telemetry
  port.

### 3. Sensing
- **Intel RealSense D435i** — depth stream + built-in IMU for Visual-Inertial
  Odometry and obstacle mapping.
- **RGB camera** (CSI or USB, e.g. Raspberry Pi Camera v2 / IMX219) — feeds the
  YOLOv8 target detection pipeline.
- **Holybro M10 GPS** — global positioning for missions, RTL, and EKF
  corrections.

### 4. Communication
- **SiK Telemetry Radio V3 (433/915 MHz)** — MAVLink to the ground station.
- **RC receiver (RadioMaster R81, SBUS)** — manual override and flight-mode
  switching.
- **WiFi/Ethernet** on the Jetson — ROS 2 bridge, imagery, and remote ops.

### 5. Power
- **4S 5200 mAh LiPo (XT60)** → **PM02 V3 power module** → **PDB**.
- PM02 supplies the Pixhawk (5 V) and reports battery voltage/current to PX4.
- PDB feeds the 4× BLHeli S 20A ESCs (XT30) → 2216 KV920 motors.
- Jetson runs on its own 5 V supply (Barrel/DC jack or dedicated 4S–5 V
  regulator) sized for the load; ground it together with the Pixhawk.

---

## Data & Control Flow

| Stream | Source → Sink | Link |
| ------ | ------------- | ---- |
| Actuator commands | Pixhawk → ESCs/Motors | FMU PWM OUT 1–4 |
| Attitude/control telemetry | Pixhawk → Ground Station | TELEM1 → SiK radio |
| ROS 2 / autonomy link | Pixhawk ↔ Jetson | TELEM2 ↔ UART ttyTHS1 |
| Manual override | RC Rx → Pixhawk | RC IN (SBUS) |
| GPS fix | GPS → Pixhawk → Jetson | GPS port / MAVLink |
| VIO + depth | RealSense D435i → Jetson | USB 3.0 |
| Detection imagery | RGB camera → Jetson | CSI/USB |

---

## See Also

- [Hardware Architecture](../hardware/README.md)
- [Bill of Materials](bom.md)
- [Wiring & Interconnects](wiring.md)
