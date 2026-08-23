# Floorplan Generator

Procedurally generates a multi-room building floor plan and exports it as an
SDF file that Gazebo can load directly. Give it a `--seed` and it produces a
layout — the same seed always gives the same building; different seeds give
different room counts, shapes, and door/window placement.

## How it works

1. **Room layout (BSP)** — the building footprint is recursively split into
   rectangular rooms using binary space partitioning. Each split creates one
   interior wall.
2. **Connectivity** — every interior wall gets exactly one door, so the
   doors form a spanning tree over the rooms: every room is reachable from
   every other room, guaranteed.
3. **Openings** — doors and windows are placed along walls while avoiding
   corners and avoiding sitting directly opposite a perpendicular wall.
4. **Walls as boxes** — every wall is axis-aligned and gets sliced into solid
   boxes around its door/window gaps (with a header above doors, a sill
   below windows).
5. **Export** — all the boxes become `<collision>`/`<visual>` pairs in a
   single static SDF `<model>` (optionally wrapped in a full `<world>` with
   a sun light and ground plane), plus a floor slab, a translucent ceiling
   net, and entry/exit markers.
6. **Optional preview** — a 3D matplotlib render of the generated layout.

Arena size, room size, wall height, and clearances are clamped to a fixed
set of constants defined near the top of the script — CLI flags can't push
past them.

## Requirements

- Python 3.8+
- Standard library only, except `matplotlib` (only needed if you use `--preview`)

```bash
pip install matplotlib   # optional, only for --preview
```

## Usage

Basic run:

```bash
python3 floorplan_generator.py
```

Custom size, seed, and a preview image:

```bash
python3 floorplan_generator.py --seed 7 --width 14 --depth 10 \
    --rooms 7 --out house.sdf --world --preview preview.png
```

Different seed → different building:

```bash
python3 floorplan_generator.py --seed 8 --out house2.sdf
```

Full list of options:

```bash
python3 floorplan_generator.py --help
```

## Key options

| Flag | Default | Description |
|---|---|---|
| `--seed` | `0` | RNG seed |
| `--width` / `--depth` | `15.0` | Building footprint (m) |
| `--rooms` | `6` | Target room count |
| `--min-room` | `2.0` | Minimum room side length (m) |
| `--wall-height` | auto | Wall height (m) |
| `--wall-thickness` | `0.12` | Wall thickness (m) |
| `--door-width` | `0.9` | Door width (m) |
| `--window-width` | `1.1` | Window width (m) |
| `--max-windows-per-wall` | `0` | Windows per exterior wall (0 = none) |
| `--corridor` | off | Bias the first split into a long hallway room |
| `--model-name` | `generated_floorplan` | SDF model name |
| `--world` | off | Export a full `<world>` instead of a bare `<model>` |
| `--out` | `floorplan.sdf` | Output SDF path |
| `--preview` | none | Save a PNG preview render |

## Output

```
Wrote SDF (world) -> house.sdf
  seed=7  rooms=7  wall_boxes=42
  entry point -> (0.00, 4.00)
  exit point  -> (14.00, 7.00)
```

Load it in Gazebo:

```bash
gz sim house.sdf       # if exported with --world
gz sim -r house.sdf     # run immediately
```
