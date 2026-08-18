# Hardware INSTRUCTIONS - Holybro X500 V2 Assembly & Maintenance

Mechanical assembly, tuning, and maintenance guidelines for the X500 V2
airframe carrying the full autonomy stack.

---

## Table of Contents

1. [Tools & Supplies](#1-tools--supplies)
2. [Step 1 - Frame Assembly](#2-step-1---frame-assembly)
3. [Step 2 - Mounting the Electronics Deck](#3-step-2---mounting-the-electronics-deck)
4. [Step 3 - Payload & Camera Mounts](#4-step-3---payload--camera-mounts)
5. [Step 4 - Preflight Mechanical Checks](#5-step-4---preflight-mechanical-checks)
6. [Maintenance & Inspection](#6-maintenance--inspection)
7. [Torque & Fastener Reference](#7-torque--fastener-reference)

---

## 1. Tools & Supplies

| Tool                  | Use                                   |
| --------------------- | ------------------------------------- |
| Hex key set (1.5, 2, 2.5, 3 mm) | Frame screws, standoffs       |
| 4 mm hex / nut driver | Motor mount nuts                      |
| Thread locker (Loctite 243) | Vibration-critical screws        |
| Zip ties               | Cable routing, anti-snag              |
| Anti-vibration mounts  | Pixhawk rubber dampers (kit included) |
| Torque wrench (if available) | Verify fastener tightness        |

> Work on a clean, soft surface. Carbon fiber splinters are sharp - wear
> gloves when handling cut edges.

---

## 2. Step 1 - Frame Assembly

1. Lay out the frame kit and identify the top plate, bottom plate, four arms,
   landing gear, and center stack standoffs.
2. Assemble the arms first. Each arm locks into the fiber-reinforced nylon
   connector keyed to the top plate. **Align the motor numbers printed on the
   arms with the top plate markings** (M1 front-left, M2 front-right, M3
   rear-right, M4 rear-left).
3. Secure each arm with the supplied hex screws. Apply thread locker on
   motor-mount screws - they vibrate loose.
4. Attach the landing gear: 16 mm + 10 mm carbon tubes with the nylon tee
   connectors, fixed with hex screws. Keep gear height at 215 mm (frame spec).
5. Stack the center: battery plate (bottom) -> PDB -> bottom plate ->
   electronics deck -> top plate, separated by the 28 mm standoffs.
6. Mount the two 250 mm rail rods (10 mm diameter) on the rail system for
   payload and camera mounts.

Refer to [README.md](README.md) for the full layout diagram.

---

## 3. Step 2 - Mounting the Electronics Deck

1. **Pixhawk 6C:** mount on the rubber-damped anti-vibration plate supplied
   with the kit. The dampers isolate high-frequency vibration from the IMU.
2. **Jetson companion:** hard-mount it (no dampers) on the top plate or on a
   dedicated standoff tray. Keep it clear of the GPS mast.
3. **GPS:** install on the dedicated mast/platform, away from carbon fiber
   (EMI shielding) and away from high-current wiring and the LiPo.
4. **RealSense D435i:** mount on the 250 mm rails with the depth-camera mount
   facing forward, clear of the prop sweep circle.
5. Route ESC signal wires up through the top plate to the flight controller
   `FMU PWM OUT` ports. Leave slack for vibration; secure with zip ties.

> Verify the Pixhawk orientation arrow matches the airframe front direction
> before finalizing the mount.

---

## 4. Step 3 - Payload & Camera Mounts

- Slide the camera / payload mounts onto the 250 mm rails; lock them with the
  thumb screws or provided clamps.
- Center the payload to keep the CG near the frame center. Re-check the CG
  (see [Preflight](#5-step-4---preflight-mechanical-checks)).
- The battery rides on the battery plate; use both 25 mm straps and route
  straps through the plate slots.

---

## 5. Step 4 - Preflight Mechanical Checks

1. [ ] All arm screws tight; thread locker applied on motor mounts.
2. [ ] No loose parts after a gentle shake test.
3. [ ] Propellers installed with correct rotation and retainers seated.
4. [ ] CG check: with battery and payload installed, balance the frame on a
     finger at the center; adjust battery position if it tips.
5. [ ] Props clear the landing gear, rails, and camera mount by a safe margin.
6. [ ] Anti-vibration dampers intact; Pixhawk secure with no play.
7. [ ] All cables have strain relief and cannot reach the props.

---

## 6. Maintenance & Inspection

| Interval       | Action                                                     |
| -------------- | ---------------------------------------------------------- |
| Before each flight | Prop, arm, and fastener check; CG re-check              |
| After any crash   | Inspect arms, plates, and standoffs for cracks; re-torque |
| Weekly         | Check motor mounts, ESC connections, vibration dampers    |
| Monthly        | Clean carbon-fiber and connectors; inspect for delamination |

- Replace carbon-fiber parts showing cracks, chips, or delamination - they
  fail without warning.
- Replace propellers that are nicked, bent, or cracked.
- Keep thread locker fresh on all vibration-critical fasteners after removal.

---

## 7. Torque & Fastener Reference

| Fastener                          | Torque (approx.)      |
| --------------------------------- | --------------------- |
| Motor mount screws (M3)           | 0.4 - 0.6 N-m         |
| Arm-to-plate hex screws           | Hand tight + 1/8 turn |
| Landing gear hex screws           | Hand tight            |
| Payload rail clamps               | Hand tight            |

> Torques are approximate. Use thread locker and re-check before first flight.

---

## See Also

- [../INSTRUCTIONS.md](../INSTRUCTIONS.md) - Root build & launch instructions
- [../electronics/README.md](../electronics/README.md) - System architecture
- [../electronics/wiring.md](../electronics/wiring.md) - Wiring & interconnects
- [../electronics/bom.md](../electronics/bom.md) - Bill of materials