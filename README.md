# DAWNKEY — BLARE alarm clock

A custom BLARE alarm clock with a 12-key MX keypad, TFT display, DS3231 real-time clock, two-AA battery input and a distinctive printable case. The enclosure preview uses a black battery pod, dark display bezel and black **“for tejas”** lettering.
# gallery
<img width="1600" height="1100" alt="preview_overall" src="https://github.com/user-attachments/assets/4e825a7b-3592-4897-b150-d4890255852f" />
<img width="194" height="170" alt="Screenshot 2026-10-07 011056" src="https://github.com/user-attachments/assets/a1ad4ad6-3671-4864-80f4-2f4a52d173f4" />

## Deliverables

- **PCB source:** `PCB/DawnKey.kicad_pro`, routed `PCB/DawnKey.kicad_pcb`, placement-only backup, reproducible generator and the full BOM.
- **Fabrication:** `Production/Gerbers.zip` with copper, mask, silkscreen, board outline and separate plated/non-plated drill files; `Production/placements.csv` for assembly.
- **Enclosure:** OpenSCAD source, print-ready STLs and per-part/assembly STEP files under `CAD/`.
- **Firmware:** Arduino sketch and the key-by-key guide under `Firmware/`.
- **Build docs:** [power, wiring and button guide](Docs/Power_and_IO.md), [system block diagram](Docs/System_Architecture.png), sources, preview and preflight report.
 handoff, not a board ready to order or rely on as an alarm clock; complete full KiCad DRC, resolve the router discrepancy, inspect the boost layout and bench-test the assembled device first. The exact checks are in [`Production/Preflight.md`](Production/Preflight.md).
