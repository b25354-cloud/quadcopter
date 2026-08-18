# Bill of Materials

Complete parts list for the X500 V2 autonomous quadcopter. Quantities marked
`(inc.)` ship with the Holybro PX4 Development Kit / X500 V2 ARF Kit.

![Holybro](https://img.shields.io/badge/Holybro-X500_V2-005C9E?style=flat-square)
![PX4](https://img.shields.io/badge/PX4-v1.14+-8A2BE2?style=flat-square)
![NVIDIA Jetson](https://img.shields.io/badge/NVIDIA-Jetson-76B900?style=flat-square&logo=nvidia&logoColor=white)
![Pixhawk](https://img.shields.io/badge/Pixhawk-6C-8A2BE2?style=flat-square)
![4S](https://img.shields.io/badge/Battery-4S_LiPo-FF5A00?style=flat-square)

---

## Airframe (hardware)

| # | Item                          | Part / Spec                        | Qty | Notes                         |
| - | ----------------------------- | ---------------------------------- | --- | ----------------------------- |
| 1 | Frame kit                     | Holybro X500 V2 (SKU30120)         | 1   | CF plates, arms, landing gear |
| 2 | Rail mounting system          | 10 mm Ø × 250 mm rods              | 2   | Payload / camera mounts       |
| 3 | Depth camera mount            | Holybro RealSense mount            | 1   | Optional, sold separately     |
| 4 | Battery straps                | 25 mm                              | 2   | Included with frame           |
| 5 | Assembly tools                | Hex keys, wrenches                 | 1   | Included                      |

## Propulsion

| # | Item        | Part / Spec                  | Qty | Notes                         |
| - | ----------- | ---------------------------- | --- | ----------------------------- |
| 6 | Motor       | Holybro 2216 KV920, XT30     | 4   | (inc.) pre-wired on arms      |
| 7 | ESC         | Holybro BLHeli S 20A, XT30   | 4   | (inc.) pre-wired on arms      |
| 8 | Propeller   | 1045 with retainer           | 4+2 | (inc.) spares included        |
| 9 | PDB         | XT60 in / XT30 out           | 1   | (inc.) no-solder              |

## Flight Control & Power

| #  | Item                  | Part / Spec                       | Qty | Notes                          |
| -- | --------------------- | --------------------------------- | --- | ------------------------------ |
| 10 | Flight controller     | Holybro Pixhawk 6C                | 1   | (inc.) PX4 v1.14+ firmware     |
| 11 | Power module          | Holybro PM02 V3 (12S, 5 V 2 A)    | 1   | (inc.) powers FC, battery mon. |
| 12 | Battery               | 4S 5200 mAh 20C+ LiPo, XT60       | 1   | 3000–5000 mAh accepted         |
| 13 | Buzzer (optional)     | Pixhawk buzzer                    | 1   | Failsafe audio                 |
| 14 | Safety switch         | Pixhawk safety switch             | 1   | Included with 6C kit           |

## Positioning & Navigation

| #  | Item   | Part / Spec         | Qty | Notes                       |
| -- | ------ | ------------------- | --- | --------------------------- |
| 15 | GPS    | Holybro M10 GPS     | 1   | (inc.) M8N/M9N compatible   |
| 16 | Mag    | Internal to GPS/FC  | —   | Compass on GPS mast         |

## Companion Computer & Sensing

| #  | Item                    | Part / Spec                          | Qty | Notes                              |
| -- | ----------------------- | ------------------------------------ | --- | ---------------------------------- |
| 17 | Companion computer      | NVIDIA Jetson Orin Nano 8 GB         | 1   | Ubuntu 22.04 / JetPack 5.x         |
| 18 | Storage                 | MicroSD / NVMe SSD 256 GB+           | 1   | OS + model weights + logs          |
| 19 | VIO + depth camera      | Intel RealSense D435i                | 1   | Depth + IMU, USB3                  |
| 20 | Detection camera        | IMX219 (RPi Cam v2) / USB cam        | 1   | Feeds YOLOv8 pipeline              |
| 21 | Camera FFC/USB cable    | 15–22 cm                             | 1   | Route to Jetson                    |
| 22 | Regulator (Jetson)      | 4S–5 V/9 V step-down or USB-C PD     | 1   | Sized for Jetson + cameras         |

## Communication

| #  | Item                | Part / Spec                  | Qty | Notes                          |
| -- | ------------------- | ---------------------------- | --- | ------------------------------ |
| 23 | Telemetry radio     | Holybro SiK Radio V3         | 2   | (inc.) air + ground, 433/915 MHz|
| 24 | RC transmitter      | RadioMaster TX16S (ELRS)     | 1   | Manual override / modes        |
| 25 | RC receiver         | RadioMaster R81 (SBUS)       | 1   | Binds to TX16S                 |
| 26 | WiFi/Ethernet       | Jetson module + antenna      | 1   | ROS 2 bridge, ops link         |
| 27 | FPV video (optional) | Analog/HDVT VTX + antenna    | 1   | Not required for autonomy      |

## Cables & Consumables

| #  | Item                  | Part / Spec                         | Qty | Notes                      |
| -- | --------------------- | ----------------------------------- | --- | -------------------------- |
| 28 | Pixhawk cable set     | JST-GH cables (GPS, telemetry, RC)  | 1   | Included with 6C           |
| 29 | GPS mast / stand      | Nylon standoffs + mast              | 1   | Keep clear of CF/EMI       |
| 30 | XT60/XT30 connectors  | Spares                              | few | Field repairs              |
| 31 | LiPo charging bag     | Fireproof                            | 1   | Safety                     |

---

## Notes

- `(inc.)` = included in the Holybro **PX4 Development Kit - X500 V2** and the
  **X500 V2 ARF Kit**.
- Battery and RC transmitter/receiver are **not** included and must be
  purchased separately.
- The RealSense depth-camera mount is sold separately from Holybro; a 3D-print
  file is available on their site.
- PX4 v1.14 (or newer) is required for M10 GPS support.
