# Design sources and constraints

- BLARE Getting Started: https://blare.hackclub.com/docs/getting-started — kit includes XIAO ESP32-C3, 12 MX switches/keycaps, 12 1N4148 diodes, 2.25-inch TFT, 3.3 V piezo, display header/jumpers, and M3 case hardware.
- BLARE PCB guide: https://blare.hackclub.com/docs/pcb-design — KiCad `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, Gerber/Drill ZIP, and PCB STEP export; board under 100 mm per side.
- BLARE CAD guide: https://blare.hackclub.com/docs/cad — complete assembled STEP; separate case parts STEP or STL; switch, screen, USB and buzzer openings; M3 inserts/posts; leave at least 0.2 mm fit tolerance.
- BLARE submission guide: https://blare.hackclub.com/docs/submitting-your-project — folders `CAD`, `PCB`, `Firmware`, `Production`; `Production/gerbers.zip`; README screenshots for overall build, schematic, PCB, and case fit, plus BOM; DRC should show zero errors.
- BLARE firmware guide: https://blare.hackclub.com/docs/firmware — ST7789 panel is 76×284; display can use the documented XIAO GPIO mapping; active-low backlight.
- Seeed XIAO ESP32-C3 official hardware guide: https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/ — 5V/VBUS is a power input/output; external supply must feed it through a diode with anode at source and cathode at XIAO 5V. The 3V3 pin is regulator output, not the battery input. Seeed documents 3.7 V lithium-battery input, not direct 2×AA input.
- Texas Instruments TPS61023 datasheet: https://www.ti.com/lit/ds/symlink/tps61023.pdf — 0.5–5.5 V operating input; 1.8 V minimum startup; 2.2–5.5 V output; typical 5 V/1.5 A design is specified at 2.7–4.35 V input. For 2×AA, output current must be validated at depleted-cell voltage and actual clock load; do not assume 1.5 A at 1.8 V.
- TI TPS61022/TPS61023 layout guidelines: https://www.ti.com/lit/pdf/slvaes4 — keep the switching/current loop and output capacitors tight; route feedback away from noisy SW node.

## Battery safety/design note

A two-cell AA series pack spans roughly 1.8 V at end-of-life to about 3.3 V fresh (cell chemistry dependent). A regulated boost stage is required for the XIAO 5V pin; use an output isolation Schottky diode per Seeed. There is no onboard AA charging. Do not place raw AA voltage on XIAO 3V3 or 5V. Wi-Fi, bright TFT backlight, and buzzer duty cycle determine battery life; measure on the finished firmware/load before quoting runtime.
