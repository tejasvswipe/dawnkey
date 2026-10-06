# Release preflight and limits

## Checks performed on this release

- **KiCad native connectivity API:** the imported `PCB/DawnKey.kicad_pcb` reports **0 unconnected connections** (`GetUnconnectedCount(True) = 0`).
- **FreeRouting 2.5 on the placement-only KiCad export:** `PCB/route.log` reports **0 unrouted connections and 0 clearance violations** (score 1000/1000). `PCB/DawnKey.ses` is the resulting routing session.
- **Gerber/drill/position exports:** produced with KiCad CLI 7 from the routed board; PTH and NPTH drills are separate, in mm, absolute origin.
- **Case CAD:** OpenSCAD produced the STL parts; FreeCAD reported all eight meshes as valid and exported the individual and positioned assembly STEP files.

## Important unresolved discrepancy

I also exported a fresh Specctra DSN from the **imported final `.kicad_pcb`** and re-ran FreeRouting on that round-tripped board. KiCad still reported 0 unconnected connections, but FreeRouting reported **5 unrouted items and 0 clearance violations**. This disagreement is not resolved. The placement-board router result and the KiCad connectivity graph are encouraging, but they do not prove that every imported copper endpoint is interpreted identically by both tools.

## Required before fabrication or daily use

1. Open the final project in a current KiCad version, run the full native **DRC**, inspect the ratsnest and inspect the buzzer, underside pull-ups, battery boost and display connections.
2. Review the Gerbers in the intended board house’s viewer.
3. Verify the actual TFT, 2-AA holder, MX switches, heat-set inserts and case clearances with physical components; the enclosure has not been test-fitted.
4. The Arduino toolchain/libraries were not available here, so the firmware was **not compiled or uploaded**. Compile for the Seeed XIAO ESP32-C3 and test every mode before assembly use.
5. No physical PCB has been fabricated or bench-tested. Check the 5 V/3.3 V rails with a current-limited supply before installing cells; do not rely on this prototype as a tested alarm clock yet.

The installed KiCad 7 command-line interface does not provide `kicad-cli pcb drc`; therefore no full KiCad DRC result is claimed. Treat this package as a complete design handoff/prototype, **not as a certified or production-released board**.