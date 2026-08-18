# Electronics INSTRUCTIONS - Wiring, Configuration & Bring-Up

Step-by-step wiring, firmware, and system bring-up guidelines for the
electronics stack (Pixhawk 6C + Jetson companion + sensors).

---

## Table of Contents

1. [Safety Rules](#1-safety-rules)
2. [Step 1 - Wiring](#2-step-1---wiring)
3. [Step 2 - Power-Up Sequence](#3-step-2---power-up-sequence)
4. [Step 3 - PX4 Firmware & Airframe](#4-step-3---px4-firmware--airframe)
5. [Step 4 - Calibration](#5-step-4---calibration)
6. [Step 5 - Companion Computer Setup](#6-step-5---companion-computer-setup)
7. [Step 6 - Link Verification](#7-step-6---link-verification)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Safety Rules

- **Always power off before wiring.**
- Verify polarity twice - reversed power destroys electronics.
- Never connect the LiPo while handling low-voltage signal wiring.
- Work with propellers removed during all bring-up and calibration steps.

---

## 2. Step 1 - Wiring

Follow the full connection map in [wiring.md](wiring.md). Quick reference:

| Port (Pixhawk 6C) | Connected To              | Notes                          |
| ----------------- | ------------------------- | ------------------------------ |
| FMU PWM OUT 1-4   | ESC signal 1-4            | White signal wire faces up     |
| TELEM1            | SiK Radio V3 (air)        | MAVLink to ground station      |
| TELEM2            | Jetson UART `ttyTHS1`     | MAVLink / uXRCE-DDS to ROS 2   |
| GPS               | Holybro M10 GPS           | UART + I2C compass             |
| RC IN             | R81 receiver (SBUS)       | Manual override, flight modes  |
| POWER             | PM02 V3 power module      | Battery monitoring + 5 V FC    |
| USB-C             | QGroundControl (setup)    | Firmware, calibration          |

Power flow: `4S LiPo (XT60)` -> `PM02 V3` -> `PDB` -> `XT30` -> `ESC M1..M4`
-> `Motors`. The Jetson is powered from its **own** regulator (4S-5 V/9 V or
USB-C PD) with a common ground shared with the Pixhawk.

Run the [wiring checklist](wiring.md#wiring-checklist) before powering up.

---

## 3. Step 2 - Power-Up Sequence

1. Connect the battery **last**, after all low-voltage wiring is verified.
2. Confirm the Pixhawk's power LED and the safety switch LED behavior.
3. Check the Jetson boots (fan / status LEDs).
4. Verify QGroundControl connects over USB-C and shows the vehicle.

---

## 4. Step 3 - PX4 Firmware & Airframe

1. Open QGroundControl -> **Firmware** -> flash PX4 **v1.14+** (required for
   M10 GPS support).
2. **Airframe:** select `Holybro 500 V2` (`Quadrotor x`). The default actuator
   mapping matches the X500 V2 wiring.
3. **Battery:** configure voltage/current scales under **Power** to match the
   PM02 V3 and the 4S battery.
4. **RC:** bind the R81 to the TX16S first; verify channels in the **Radio**
   setup. Configure flight modes (Position / Altitude / Manual) and the
   failsafe.

---

## 5. Step 4 - Calibration

In QGroundControl, run calibrations in this order:

1. **Sensors** - accelerometer (6-side), gyroscope, level horizon.
2. **Compass** - rotate the airframe through all axes; keep it clear of
   carbon fiber, magnets, and high-current wiring.
3. **Radio** - full-stick sweep; verify throws and mode switches.
4. **ESC / Motor test** (props OFF) - verify motor order M1-M4 and rotation
   directions match the layout:
   - M1 front-left CW, M2 front-right CCW, M3 rear-right CW, M4 rear-left CCW.
5. **Power** - confirm voltage and current readings against a multimeter.

---

## 6. Step 5 - Companion Computer Setup

1. Install Ubuntu 22.04 / JetPack 5.x and ROS 2 Humble on the Jetson.
2. Build the workspace (see [../INSTRUCTIONS.md](../INSTRUCTIONS.md)).
3. Set TELEM2 baud to `921600` in PX4 (`PX4_SER_TEL2_BAUD=921600`) and start
   the MicroXRCE-DDS agent:

```bash
micro-ros-agent serial --dev /dev/ttyTHS1 -b 921600
```

4. Configure USB permission so the RealSense and IMX219 camera streams appear
   (`lsusb`, `ls /dev/video*`).
5. Confirm the ground station link: SiK radio on TELEM1 to the ground SiK and
   QGroundControl.

---

## 7. Step 6 - Link Verification

| Check                     | Command / Where                          | Expected                    |
| ------------------------- | ---------------------------------------- | --------------------------- |
| uXRCE-DDS topics          | `ros2 topic list | grep -E 'fmu|vehicle'` | `/fmu/...` topics present   |
| Sensor data               | `ros2 run px4_ros_com sensor_combined_listener` | Streams IMU/GPS data |
| MAVLink telemetry         | QGroundControl top bar                    | Vehicle connected           |
| Battery readout           | QGroundControl -> Power                   | Voltage/current matches     |
| Camera streams            | `ros2 run <realsense/imu> ...` or `v4l2-ctl` | Live video frame      |

Only after all checks pass, and with props removed, proceed to the ROS 2
bring-up ([quadcopter_bringup](../src/quadcopter_bringup/INSTRUCTIONS.md)).

---

## 8. Troubleshooting

| Symptom                     | Likely Cause                  | Resolution                                  |
| --------------------------- | ----------------------------- | ------------------------------------------- |
| FC does not power up        | PM02 / polarity               | Check PM02 wiring and battery voltage       |
| No GPS fix                  | Compass interference / mast   | Move GPS clear of CF; re-calibrate compass  |
| RC not detected             | SBUS wire / binding           | Re-bind; verify signal on RC IN pin 3       |
| No `/fmu/*` topics          | Agent not running / baud      | Start agent; confirm `PX4_SER_TEL2_BAUD`    |
| Erratic ESC behavior        | Motor order / rotation        | Re-run ESC calibration; verify M1-M4 order  |
| Jetson link drops           | Common ground / regulator     | Share ground; check Jetson power supply     |

---

## See Also

- [README.md](README.md) - System architecture & data flow
- [wiring.md](wiring.md) - Connection map, motor order, checklist
- [bom.md](bom.md) - Bill of materials
- [../hardware/INSTRUCTIONS.md](../hardware/INSTRUCTIONS.md) - Mechanical assembly
- [../INSTRUCTIONS.md](../INSTRUCTIONS.md) - Root build & launch instructions