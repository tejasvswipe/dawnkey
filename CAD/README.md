# DAWNKEY case and print files

The case is a **parametric prototype** for the 94 × 90 mm PCB. The concept combines a dark raised TFT visor, 4 × 3 MX switch plate, buzzer vents, neon-style accent slots, a serviceable side battery pod and the black **“for tejas”** name insert.

## Files

- `DAWNKEY_Case.scad` — editable OpenSCAD master; change its `part` variable to render `base`, `top`, `bezel`, `battery_pod`, `battery_door`, `accents`, `text`, `key_labels` or the concept assembly.
- `STL/` — individual print-ready meshes; `key_labels.stl` and `text.stl` can be printed in black or inserted as separate color parts.
- `STEP/DAWNKEY_Case_Assembly.step` — positioned faceted case assembly; individual STEP files are alongside it. The STEP shapes were converted from STL meshes, so they are faceted rather than native analytic CAD solids.
- `STEP/DawnKey_PCB.step` — board-only STEP export.
- `stl_to_step.FCMacro` — reproducible FreeCAD STL-to-STEP export macro.

## Prototype geometry

The base/plate envelope is 108 × 132 mm. The side AA pod cavity is nominally 66 × 37 × 19 mm. The top plate has four M3 clearance openings, twelve nominal 14 mm MX apertures on 19.05 mm pitch, an ST7789 viewing aperture and a vent pattern over the piezo. The case is designed around common-size components; no actual TFT, AA holder, switch or heat-set insert has been test-fitted.

## Suggested assembly and print workflow

1. Render a small test of one MX opening, one M3 post and the display/bezel interface before printing all parts.
2. Print the base, top plate, visor, battery pod and door as separate pieces. Use the accent, wordmark and key-label meshes for a second color; the intended look is a light shell with black lettering/trim and a dark battery pod/visor.
3. Test the purchased 2-AA holder in the pod and measure its switch/harness. Adjust `DAWNKEY_Case.scad` if its actual dimensions differ from the nominal cavity.
4. Fit the TFT with the real panel PCB/cable; confirm the USB-C access slot and all four M3 inserts before final assembly.
5. Only then use the print-ready files for a full case.

The case render is a design visualization, **not proof of fit**. Check tolerances against your printer, filament shrinkage and actual parts.