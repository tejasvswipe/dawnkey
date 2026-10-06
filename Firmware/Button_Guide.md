# DAWNKEY button guide

The twelve MX switches are arranged **4 columns × 3 rows**, viewed from the front. Read left-to-right, top-to-bottom:

| Physical key | Label | Normal clock view | Setting mode | When the alarm is ringing |
|---|---:|---|---|---|
| SW01 | `1` | No action | Enters digit 1 | Enters digit 1 of the wake code |
| SW02 | `2` | No action | Enters digit 2 | Enters digit 2 of the wake code |
| SW03 | `3` | No action | Enters digit 3 | Enters digit 3 of the wake code |
| SW04 | `4` | No action | Enters digit 4 | Enters digit 4 of the wake code |
| SW05 | `5` | No action | Enters digit 5 | Enters digit 5 of the wake code |
| SW06 | `6` | No action | Enters digit 6 | Enters digit 6 of the wake code |
| SW07 | `7` | No action | Enters digit 7 | Enters digit 7 of the wake code |
| SW08 | `8` | No action | Enters digit 8 | Enters digit 8 of the wake code |
| SW09 | `9` | No action | Enters digit 9 | Enters digit 9 of the wake code |
| SW10 | `0` | No action | Enters digit 0 | Enters digit 0 of the wake code |
| SW11 | `SNOOZE` | Short press changes the display page; hold ~0.85 s to set the RTC clock (`HHMM`) | Short press clears the current entry | Short press snoozes for 5 minutes; hold is not a snooze shortcut |
| SW12 | `STOP/OK` | Short press toggles alarm on/off; hold ~0.85 s to set the alarm time (`HHMM`) | Saves a valid four-digit `HHMM` entry | Checks the four-digit dismiss code and stops the alarm only if correct |

## Wake challenge

The starter sketch uses **3141** as the example alarm-dismiss code. Change `DISMISS_CODE` near the top of `DAWNKEY.ino` if you want another code, then upload the sketch again. During ringing, enter four digits using SW01–SW10, then press SW12. An incorrect code clears the entry and the alarm continues. SW11 gives one 5-minute snooze.

## Setting the clock and alarm

- Hold **SW11** for about 0.85 seconds, enter four digits as 24-hour `HHMM`, then press **SW12** to set the current clock time. The date is retained from the RTC; if the RTC has lost power, its date is initialized from the firmware compile timestamp.
- Hold **SW12** for about 0.85 seconds, enter the new alarm `HHMM`, then press **SW12** to save and enable it.
- In either setting mode, press **SW11** to clear the partially typed value. Values outside `00:00`–`23:59` are rejected.
- The default alarm is **07:00 and enabled**. A short press of SW12 toggles it.

The screen/backlight is always on in this starter firmware. It avoids Wi-Fi to reduce power draw, but no battery-runtime claim has been measured.
