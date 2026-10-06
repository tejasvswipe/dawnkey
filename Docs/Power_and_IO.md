# DAWNKEY power, wiring and controls

## 1. Two-AA power path

Use a **two-cell AA holder wired in series** with a 2-pin JST-PH lead. The PCB connector is `J3`:

| J3 pin | PCB net | Connect to |
|---|---|---|
| 1 | `BAT_RAW` | Positive from the battery holder, through an inline SPST on/off switch |
| 2 | `GND` | Battery-holder negative |

The board uses a **TPS61023 boost converter** to make a regulated nominal 5 V rail (`BOOST_5V`). Its output reaches the Seeed XIAO ESP32-C3 5V pad through **D13, an SS14 Schottky diode**. The diode is oriented with its anode at `BOOST_5V` and cathode at `USB_5V` / the XIAO 5V pad. The XIAO’s onboard regulator then supplies the 3.3 V rail used by the RTC, GPIO expander, display logic and buzzer.

**Important:** raw AA voltage must never be connected directly to the XIAO 3V3 pin or directly to its 5V pin. The cells are primary power sources; the PCB does **not** charge NiMH cells. Use a matched pair of the same chemistry and state of charge. Before inserting cells, check polarity, inspect U4/L1/D13 orientation, and measure the boosted output and the diode-side XIAO input with a current-limited bench supply. Test USB-versus-battery behavior on the bench; do not assume it is safe until verified on the assembled board.

The DS3231 `VBAT` pin is tied to ground because the AA pack is intended to remain the clock’s always-on supply. **If the AA pack is removed, the RTC time will be lost** (the firmware initializes the date/time from its compile timestamp at next start). This design has no separate coin-cell backup.

## 2. Signal and connector map

### XIAO ESP32-C3

| XIAO Arduino pin | Role | Routed net |
|---|---|---|
| D0 | TFT SCLK | `TFT_SCLK` |
| D1 | TFT MOSI | `TFT_MOSI` |
| D2 | TFT reset | `TFT_RST` |
| D3 | TFT data/command | `TFT_DC` |
| D4 | TFT chip select | `TFT_CS` |
| D5 | TFT backlight enable | `TFT_BL` (active-low on the BLARE panel) |
| D6 | I²C clock | `I2C_SCL` |
| D7 | I²C data | `I2C_SDA` |
| D10 | Piezo driver control | `BUZZER_CTL` |
| 5V | Boost/USB input | `USB_5V` through D13 from battery boost |
| 3V3 | Regulated output | `3V3` |
| GND | Common return | `GND` |

GPIO8/GPIO9 are deliberately left unused because of ESP32-C3 boot-strapping considerations.

### TFT header J1

The 8-pin BLARE/ST7789 header order is **GND, 3V3, SCLK, MOSI, RST, DC, CS, BL**. The display is an external module connected with the kit jumper wires; it is not soldered flat to the PCB.

### I²C devices and expansion J2

- U2 MCP23017: address `0x20`; GPIO expander for the keypad.
- U3 DS3231: address `0x68`; clock/alarm time source.
- Pull-ups R4/R5: 4.7 kΩ from SDA/SCL to 3V3.
- J2 pins 1–4: **3V3, GND, SDA, SCL**. This is a low-current sensor/accessory header, not a general-purpose power output.

R3–R5 are non-polar 0603 resistors. Their PCB pad numbering is intentionally exchanged to compensate for the underside autorouter/import transform; electrically, each resistor still connects the signal named in the BOM to 3V3. There is no physical resistor polarity or orientation requirement.

### Key matrix

U2 GPA0–GPA3 are columns 0–3; GPA4–GPA6 are rows 0–2. One 1N4148 diode is fitted per MX-style switch to prevent matrix ghosting. The diode direction is from each row toward its switch/column node as shown by the PCB net assignments.

## 3. Every button

Viewed from the front with the display above the keypad, read left-to-right and top-to-bottom:

| Position / label | Normal clock screen | While setting time/alarm | While ringing |
|---|---|---|---|
| Top row: `1`, `2`, `3`, `4` | No action | Enters that digit | Enters that digit into the dismiss code |
| Middle row: `5`, `6`, `7`, `8` | No action | Enters that digit | Enters that digit into the dismiss code |
| Bottom-left: `9` | No action | Enters 9 | Enters 9 into the dismiss code |
| Bottom, second: `0` | No action | Enters 0 | Enters 0 into the dismiss code |
| Bottom, third: `S` / Snooze (SW11) | Short press changes the display page; hold about 0.85 s to set the RTC clock | Short press clears the typed entry | Short press silences the buzzer and snoozes for 5 minutes |
| Bottom-right: `OK` / Stop (SW12) | Short press toggles the alarm on/off; hold about 0.85 s to set the alarm time | Saves a valid four-digit `HHMM` value | Stops only after the four-digit code is entered and confirmed |

The starter firmware’s example dismiss code is **3141**. While ringing, type the four digits with keys 1–0 and press `OK`. A wrong code clears the entry but leaves the alarm active. The default alarm is **07:00 and enabled**. In either setting mode, enter 24-hour `HHMM` using the number keys; invalid hour/minute values are rejected.

## 4. Bring-up checklist

1. Assemble the board without batteries. Inspect solder bridges, polarity, connector pin order, U4, L1 and D13.
2. Power through a current-limited bench supply at J3. Confirm the boost and diode-side rail before attaching the XIAO or display.
3. Scan I²C: expect MCP23017 `0x20` and DS3231 `0x68`.
4. Verify the display pin order/backlight polarity and test every matrix key individually.
5. Confirm buzzer switching, RTC time setting, alarm setting, snooze, wake-code dismissal, and both USB/battery source modes.
6. Measure battery current and runtime with the actual TFT backlight and alarm duty cycle. Runtime has not yet been measured; the starter sketch keeps the backlight on.

This is a prototype package. No physical board has been fabricated or bench-tested here; inspect the KiCad DRC report and verify current, voltage, thermal behavior and mechanical fit before relying on it as a daily alarm.
