# PCB production outputs

`Gerbers.zip` is the standard two-layer fabrication package. It contains the front/back copper, solder-mask and silkscreen layers, the Edge.Cuts outline, the Excellon plated (`PTH`) and non-plated (`NPTH`) drill files, KiCad’s Gerber job file, and SVG drill maps. Drill coordinates are in millimeters with absolute origin.

`placements.csv` is the component placement export for assembly. `pad_net_map.csv` is the component pad/net reference for review.

The board outline is nominally 94 × 90 mm with four M3-clearance holes. Before placing a manufacturing order, inspect the archive in the chosen fab’s Gerber viewer and confirm the material/thickness, copper weight, finish, tolerances, drill registration, and component clearances with that fab. The design has not been fabricated or electrically bench-tested; see `Preflight.md`. The native KiCad DRC is still required before manufacture.