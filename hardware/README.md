# Hardware Architecture — Holybro X500 V2

The physical platform is built on the **Holybro X500 V2** airframe — a 500 mm
wheelbase carbon-fiber professional quadcopter. It is sized to carry the full
autonomy stack (flight controller, Jetson companion computer, depth camera,
GPS, telemetry, and a 4S battery) while keeping ~1.5 kg of usable payload.

![Holybro](https://img.shields.io/badge/Holybro-X500_V2-005C9E?style=flat-square)
![Frame](https://img.shields.io/badge/Frame-Carbon_Fiber-3C3C3C?style=flat-square)
![Wheelbase](https://img.shields.io/badge/Wheelbase-500_mm-009FB7?style=flat-square)
![Motors](https://img.shields.io/badge/Motors-2216_KV920-F0A500?style=flat-square)
![ESC](https://img.shields.io/badge/ESC-BLHeli_S_20A-00A859?style=flat-square)
![Props](https://img.shields.io/badge/Props-1045-7C4DFF?style=flat-square)
![Battery](https://img.shields.io/badge/Battery-4S_LiPo-FF5A00?style=flat-square)

---

## Frame Specifications

| Parameter                | Value                                       |
| ------------------------ | ------------------------------------------- |
| Wheelbase                | 500 mm                                      |
| Frame body               | 144 × 144 mm, 2 mm carbon-fiber plates      |
| Arm                      | 16 mm Ø carbon-fiber tubes                  |
| Motor mount pattern      | 16 × 16 mm and 19 × 19 mm                   |
| Landing gear height      | 215 mm                                      |
| Plate spacing            | 28 mm                                       |
| Rail mounting system     | Dual 10 mm Ø × 250 mm carbon rods           |
| Frame weight             | ~610 g                                      |
| Recommended battery      | 4S 3000–5000 mAh 20C+ (XT60)                |
| Hover flight time        | ~18 min (4S 5000 mAh, no payload)           |
| Max payload              | ~1.5 kg (4S 5000 mAh, 70% throttle)         |

---

## Frame Layout

```
        [M1]                       [M2]
         CW           (front)        CCW
          \_______________/
          |               |           <- top plate (144x144 mm)
          |    PDB  +     |           <- center stack (28 mm)
          |   Pixhawk 6C  |
          |   Jetson      |           <- companion mount
          |   GPS mast    |
          |_______________|
          /               \
        [M4]                       [M3]
        CCW           (rear)        CW

    M1: front-left  CW  — prop M1
    M2: front-right CCW — prop M2
    M3: rear-right  CW  — prop M3
    M4: rear-left   CCW — prop M4
```

- **X configuration** (front = direction of the arrow on the top plate).
- Motor numbering and rotation follow PX4 default for the `Holybro 500 V2`
  airframe (`Quadrotor x`).
- Motor signal leads route through the top plate to the flight controller
  `FMU PWM OUT` ports.
- The center stack carries, bottom to top: battery plate, PDB, bottom plate,
  electronics deck (Pixhawk, Jetson), top plate, GPS mast.
- The 250 mm rails accept the depth-camera mount (Intel RealSense) and any
  auxiliary payload fixtures.

---

## Propulsion

| Component | Part | Quantity |
| --------- | ---- | -------- |
| Motor     | Holybro 2216 KV920 (XT30) | 4 |
| ESC       | Holybro BLHeli S 20A (XT30) | 4 |
| Propeller | 1045 (10 × 4.5") with retainer | 4 + spares |
| PDB       | XT60 battery input, XT30 ESC outputs | 1 |

- Motors and ESCs arrive pre-wired on the arms with XT30 connectors — no
  soldering required.
- ESC signal wires are routed up through the top plate to the flight
  controller.
- Propeller rotation pairs CW/CCW as shown in the layout diagram.

---

## Mechanical Assembly Notes

- Landing gear: 16 mm + 10 mm carbon tubes with reinforced nylon tee
  connectors, fixed with hex screws.
- Arms lock into fiber-reinforced nylon connectors keyed to the top plate;
  align the motor numbers printed on the arms with the top plate markings.
- Payload / battery boards are joined to the bottom plate with nylon standoffs.
- Mount the GPS on the dedicated mast/platform to keep it clear of carbon-fiber
  (EMI shielding) and high-current wiring.
- Anti-vibration: use the rubber-damped mounts supplied with the Pixhawk kit for
  the flight controller; hard-mount the Jetson.

---

## See Also

- [Electronics Architecture](../electronics/README.md)
- [Bill of Materials](../electronics/bom.md)
- [Wiring & Interconnects](../electronics/wiring.md)
