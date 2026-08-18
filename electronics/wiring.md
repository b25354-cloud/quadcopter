# Wiring & Interconnects

Connection map for the X500 V2 autonomy stack. Always power off before
wiring. Verify polarity twice — reversed power destroys electronics.

![Holybro](https://img.shields.io/badge/Holybro-X500_V2-005C9E?style=flat-square)
![Pixhawk](https://img.shields.io/badge/Pixhawk-6C-8A2BE2?style=flat-square)
![MAVLink](https://img.shields.io/badge/MAVLink-2-1479D1?style=flat-square)
![SBUS](https://img.shields.io/badge/RC-SBUS-EF3E2B?style=flat-square)
![XT60](https://img.shields.io/badge/Power-XT60-FF5A00?style=flat-square)

---

## Pixhawk 6C Port Map

| Port   | Connected To              | Notes                              |
| ------ | ------------------------- | ---------------------------------- |
| FMU PWM OUT 1–4 | ESC signal 1–4    | White signal wire faces up         |
| TELEM1 | SiK Radio V3 (air)       | MAVLink to ground station          |
| TELEM2 | Jetson UART `ttyTHS1`    | MAVLink/µXRCE-DDS to ROS 2         |
| GPS    | Holybro M10 GPS          | UART + I2C compass                 |
| RC IN  | R81 receiver (SBUS)      | Manual override, flight modes      |
| POWER  | PM02 V3 power module     | Battery voltage/current + 5 V FC   |
| I2C    | (optional) external sensors | Keep unpopulated if unused       |
| USB-C  | QGroundControl (setup)   | Firmware, calibration, tuning      |

---

## Power Flow

```
4S LiPo (XT60)
    │
    ▼
PM02 V3 ── 5V/2A ───────► Pixhawk 6C (POWER)
    │
    ▼
PDB (XT60 in) ──► XT30 ──► ESC M1 ──► Motor 1
             ├──► XT30 ──► ESC M2 ──► Motor 2
             ├──► XT30 ──► ESC M3 ──► Motor 3
             └──► XT30 ──► ESC M4 ──► Motor 4

Jetson ── 5V/9V regulator ──► from 4S balance/XT60 tap (or USB-C PD)
```

- ESC signal grounds are shared with the Pixhawk via the PWM connectors.
- The PDB has dedicated 5 V (and optional 9/12 V) pads for auxiliaries — use
  for the buzzer and safety LED only, not for the Jetson.

---

## Signal & Data Flow

| From                 | To                      | Cable / Link                | Notes                            |
| -------------------- | ----------------------- | --------------------------- | -------------------------------- |
| Pixhawk TELEM1       | SiK Radio (air)         | JST-GH 4-pin               | 433/915 MHz link to GCS          |
| Pixhawk TELEM2       | Jetson UART             | JST-GH → UART (ttyTHS1)    | `PX4_SER_TEL2_BAUD=921600`, µXRCE|
| Pixhawk FMU OUT 1–4  | ESC signal               | 3-pin PWM (white up)       | Order matches motor numbering    |
| GPS                  | Pixhawk GPS port         | JST-GH 6-pin               | Compass on the mast              |
| R81 receiver         | Pixhawk RC IN            | SBUS (signal on pin 3)     | Bind first, verify in QGC        |
| RealSense D435i      | Jetson                   | USB 3.0                    | Depth + IMU streams              |
| IMX219 camera        | Jetson CSI               | 15-pin FFC                 | YOLOv8 detection feed            |
| Jetson               | Ground station           | WiFi/Ethernet              | ROS 2 topics, imagery            |

---

## Motor Order & Rotation (Pixhawk 6C, X configuration)

| Motor | Position     | Rotation | Prop |
| ----- | ------------ | -------- | ---- |
| M1    | Front-left   | CW  (spin)  | 1045 |
| M2    | Front-right  | CCW        | 1045 |
| M3    | Rear-right   | CW         | 1045 |
| M4    | Rear-left    | CCW        | 1045 |

Match the labels printed on the X500 V2 arms to the top plate. Select the
**Holybro 500 V2** airframe in QGroundControl; the default actuator mapping
already matches this wiring.

---

## Wiring Checklist

1. [ ] Arms plugged into PDB with XT30 connectors, ESC signal wires routed up.
2. [ ] ESC 1–4 into FMU PWM OUT 1–4 (white up), motor order verified.
3. [ ] PM02 → Pixhawk POWER; battery plugged only after all low-voltage wiring done.
4. [ ] GPS on mast, connected to GPS port; compass clear of CF and motor leads.
5. [ ] SiK radio on TELEM1; Jetson on TELEM2 with proper baud.
6. [ ] R81 receiver on RC IN; verified in QGroundControl Radio Setup.
7. [ ] Jetson powered from its own regulator; common ground shared with Pixhawk.
8. [ ] RealSense and detection camera plugged into Jetson, drivers confirmed.
9. [ ] Battery voltage and current reading correctly in QGC.
10. [ ] Propellers installed with correct rotation/retainers, safety switch ON.
