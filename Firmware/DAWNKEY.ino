/*
  DAWNKEY — BLARE alarm clock firmware
  Board: Seeed XIAO ESP32-C3 + MCP23017 (0x20) + DS3231 (0x68)
  Screen: ST7789 76x284, BL active-low
  Key matrix: MCP GPA0..3 = columns; GPA4..6 = rows; 1N4148 diodes
  Power: two AA cells -> TPS61023 5V boost -> series Schottky -> XIAO 5V

  Install Arduino libraries:
    Adafruit GFX Library
    Adafruit ST7735 and ST7789 Library
    Adafruit MCP23017 Arduino Library
    RTClib by Adafruit
*/
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <Adafruit_MCP23X17.h>
#include <RTClib.h>
#include <Preferences.h>

// BLARE firmware guide pin assignments for the display.
#define TFT_SCLK 0
#define TFT_MOSI 1
#define TFT_RST  2
#define TFT_DC   3
#define TFT_CS   4
#define TFT_BL   5
// Main PCB routes the transistor buzzer control to XIAO D10 (GPIO10),
// deliberately avoiding the GPIO8/GPIO9 boot-strapping pins.
#define BUZZER_PIN D10
// I2C uses the XIAO pads routed to D7 (SDA) and D6 (SCL), not the TFT pins.
#define I2C_SDA_PIN D7
#define I2C_SCL_PIN D6

class DawnKeyST7789 : public Adafruit_ST7789 {
 public:
  DawnKeyST7789(int8_t cs, int8_t dc, int8_t mosi, int8_t sclk, int8_t rst)
      : Adafruit_ST7789(cs, dc, mosi, sclk, rst) {}
  void setOffsets(uint8_t col, uint8_t row) {
    _colstart = _colstart2 = col;
    _rowstart = _rowstart2 = row;
  }
};

DawnKeyST7789 tft(TFT_CS, TFT_DC, TFT_MOSI, TFT_SCLK, TFT_RST);
Adafruit_MCP23X17 mcp;
RTC_DS3231 rtc;
Preferences prefs;

constexpr uint8_t MCP_ADDR = 0x20;
constexpr uint8_t COLS[4] = {0, 1, 2, 3};
constexpr uint8_t ROWS[3] = {4, 5, 6};
constexpr uint32_t DEBOUNCE_MS = 28;
constexpr uint32_t LONG_PRESS_MS = 850;
constexpr uint32_t SNOOZE_SECONDS = 5 * 60;
const char *DISMISS_CODE = "3141";  // Change this in code if desired.
const char *KEYS[12] = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "SNOOZE", "STOP/OK"};

enum UiMode : uint8_t { NORMAL, SET_ALARM, SET_CLOCK, RINGING };
UiMode mode = NORMAL;

bool rawState[12] = {};
bool stableState[12] = {};
uint32_t rawChangedAt[12] = {};
uint32_t keyDownAt[12] = {};
uint8_t alarmHour = 7;
uint8_t alarmMinute = 0;
bool alarmEnabled = true;
uint8_t screenPage = 0;
String digits;
String alarmCode;
bool alarmHasTriggeredToday = false;
bool snoozeArmed = false;
uint32_t snoozeAt = 0;
uint32_t lastUiDraw = 0;
uint32_t lastAlarmCheck = 0;
uint32_t lastBeep = 0;
bool beepPhase = false;

String twoDigits(uint8_t n) { return (n < 10 ? "0" : "") + String(n); }

void drawNormal() {
  DateTime now = rtc.now();
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextColor(ST77XX_CYAN, ST77XX_BLACK);
  tft.setTextSize(2);
  tft.setCursor(6, 5);
  tft.print("DAWNKEY");
  tft.setTextColor(ST77XX_WHITE, ST77XX_BLACK);
  tft.setTextSize(3);
  tft.setCursor(6, 28);
  tft.print(twoDigits(now.hour()) + ":" + twoDigits(now.minute()));
  tft.setTextSize(1);
  tft.setCursor(166, 9);
  tft.setTextColor(alarmEnabled ? ST77XX_GREEN : ST77XX_RED, ST77XX_BLACK);
  tft.print(alarmEnabled ? "ALARM ON" : "ALARM OFF");
  tft.setCursor(166, 26);
  tft.setTextColor(ST77XX_WHITE, ST77XX_BLACK);
  tft.print("WAKE " + twoDigits(alarmHour) + ":" + twoDigits(alarmMinute));
  tft.setCursor(166, 44);
  if (screenPage == 0) {
    tft.print("HOLD SNOOZE: SET TIME");
  } else {
    tft.print("HOLD STOP: SET ALARM");
  }
  tft.setCursor(6, 63);
  tft.setTextColor(ST77XX_YELLOW, ST77XX_BLACK);
  tft.print("11 SNOOZE / 12 STOP");
}

void drawEntry(const char *title) {
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextColor(ST77XX_MAGENTA, ST77XX_BLACK);
  tft.setTextSize(2);
  tft.setCursor(8, 7);
  tft.print(title);
  tft.setTextColor(ST77XX_WHITE, ST77XX_BLACK);
  tft.setTextSize(3);
  tft.setCursor(8, 37);
  String shown = digits;
  while (shown.length() < 4) shown += "_";
  tft.print(shown.substring(0, 2) + ":" + shown.substring(2, 4));
  tft.setTextSize(1);
  tft.setCursor(170, 49);
  tft.print("1-0 type  HHMM");
  tft.setCursor(170, 63);
  tft.print("12 save  11 clear");
}

void drawRinging() {
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextColor(ST77XX_RED, ST77XX_BLACK);
  tft.setTextSize(3);
  tft.setCursor(12, 6);
  tft.print("WAKE UP!");
  tft.setTextColor(ST77XX_WHITE, ST77XX_BLACK);
  tft.setTextSize(2);
  tft.setCursor(12, 39);
  tft.print("CODE: ");
  for (uint8_t i = 0; i < alarmCode.length(); ++i) tft.print("*");
  for (uint8_t i = alarmCode.length(); i < 4; ++i) tft.print("_");
  tft.setTextSize(1);
  tft.setCursor(12, 66);
  tft.print("11 snoozes 5m | enter 3141 then 12");
}

void drawUi() {
  if (mode == NORMAL) drawNormal();
  else if (mode == SET_ALARM) drawEntry("SET ALARM");
  else if (mode == SET_CLOCK) drawEntry("SET CLOCK");
  else drawRinging();
}

void saveAlarm() {
  prefs.putUChar("ah", alarmHour);
  prefs.putUChar("am", alarmMinute);
  prefs.putBool("ae", alarmEnabled);
}

bool parseHHMM(uint8_t &hh, uint8_t &mm) {
  if (digits.length() != 4) return false;
  hh = digits.substring(0, 2).toInt();
  mm = digits.substring(2, 4).toInt();
  return hh < 24 && mm < 60;
}

void stopAlarm() {
  noTone(BUZZER_PIN);
  mode = NORMAL;
  snoozeArmed = false;
  alarmCode = "";
  alarmHasTriggeredToday = true;
  drawUi();
}

void startAlarm() {
  mode = RINGING;
  alarmCode = "";
  snoozeArmed = false;
  lastBeep = 0;
  drawUi();
}

void enterSetMode(UiMode target) {
  noTone(BUZZER_PIN);
  digits = "";
  mode = target;
  drawUi();
}

void appendDigit(uint8_t key) {
  const char *d = (key == 9) ? "0" : String(key + 1).c_str();
  if (digits.length() < 4) digits += d;
}

void onKey(uint8_t key, uint32_t heldMs) {
  if (key < 10) {
    const char *d = (key == 9) ? "0" : nullptr;
    if (mode == SET_ALARM || mode == SET_CLOCK) {
      if (key == 9) digits += "0";
      else digits += String(key + 1);
      if (digits.length() > 4) digits.remove(4);
      drawUi();
    } else if (mode == RINGING) {
      if (key == 9) alarmCode += "0";
      else alarmCode += String(key + 1);
      if (alarmCode.length() > 4) alarmCode.remove(4);
      drawUi();
    }
    (void)d;
    return;
  }

  if (key == 10) {  // Button 11: SNOOZE / CLOCK SET
    if (mode == RINGING) {
      noTone(BUZZER_PIN);
      mode = NORMAL;
      snoozeArmed = true;
      snoozeAt = rtc.now().unixtime() + SNOOZE_SECONDS;
      drawUi();
    } else if (mode == SET_ALARM || mode == SET_CLOCK) {
      digits = "";
      drawUi();
    } else if (heldMs >= LONG_PRESS_MS) {
      enterSetMode(SET_CLOCK);
    } else {
      screenPage ^= 1;
      drawUi();
    }
    return;
  }

  // Button 12: STOP / OK / ALARM SET
  if (mode == RINGING) {
    if (alarmCode == DISMISS_CODE) stopAlarm();
    else {
      alarmCode = "";
      drawUi();
    }
  } else if (mode == SET_ALARM || mode == SET_CLOCK) {
    uint8_t hh, mm;
    if (!parseHHMM(hh, mm)) {
      digits = "";
      drawUi();
      return;
    }
    if (mode == SET_ALARM) {
      alarmHour = hh;
      alarmMinute = mm;
      alarmEnabled = true;
      saveAlarm();
    } else {
      DateTime now = rtc.now();
      rtc.adjust(DateTime(now.year(), now.month(), now.day(), hh, mm, 0));
    }
    digits = "";
    mode = NORMAL;
    drawUi();
  } else if (heldMs >= LONG_PRESS_MS) {
    enterSetMode(SET_ALARM);
  } else {
    alarmEnabled = !alarmEnabled;
    saveAlarm();
    drawUi();
  }
}

void scanKeys() {
  uint32_t now = millis();
  for (uint8_t c = 0; c < 4; ++c) {
    mcp.pinMode(COLS[c], OUTPUT);
    mcp.digitalWrite(COLS[c], LOW);
    delayMicroseconds(40);
    for (uint8_t r = 0; r < 3; ++r) {
      uint8_t i = r * 4 + c;
      bool raw = (mcp.digitalRead(ROWS[r]) == LOW);
      if (raw != rawState[i]) {
        rawState[i] = raw;
        rawChangedAt[i] = now;
      }
      if ((now - rawChangedAt[i]) >= DEBOUNCE_MS && stableState[i] != rawState[i]) {
        stableState[i] = rawState[i];
        if (stableState[i]) keyDownAt[i] = now;
        else onKey(i, now - keyDownAt[i]);
      }
    }
    mcp.pinMode(COLS[c], INPUT_PULLUP);
  }
}

void checkAlarm() {
  DateTime now = rtc.now();
  if (snoozeArmed && now.unixtime() >= snoozeAt) {
    snoozeArmed = false;
    startAlarm();
  }
  if (!alarmEnabled || mode == RINGING || snoozeArmed) return;
  if (now.hour() == alarmHour && now.minute() == alarmMinute && now.second() == 0) {
    // Stop the alarm repeating every loop through the entire matching minute.
    if (!alarmHasTriggeredToday) {
      alarmHasTriggeredToday = true;
      startAlarm();
    }
  }
  if (now.hour() == 0 && now.minute() == 0 && now.second() == 1) {
    alarmHasTriggeredToday = false;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, LOW);  // BLARE TFT backlight is active-low.
  pinMode(BUZZER_PIN, OUTPUT);
  noTone(BUZZER_PIN);

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  if (!mcp.begin_I2C(MCP_ADDR, &Wire)) {
    Serial.println("ERROR: MCP23017 not found at 0x20");
  } else {
    for (uint8_t c = 0; c < 4; ++c) mcp.pinMode(COLS[c], INPUT_PULLUP);
    for (uint8_t r = 0; r < 3; ++r) mcp.pinMode(ROWS[r], INPUT_PULLUP);
  }

  if (!rtc.begin(&Wire)) Serial.println("ERROR: DS3231 not found at 0x68");
  else if (rtc.lostPower()) rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  prefs.begin("dawnkey", false);
  alarmHour = prefs.getUChar("ah", 7);
  alarmMinute = prefs.getUChar("am", 0);
  alarmEnabled = prefs.getBool("ae", true);

  tft.init(76, 284);
  tft.setOffsets(82, 18);
  tft.invertDisplay(false);
  tft.setRotation(1);
  drawUi();
}

void loop() {
  scanKeys();
  uint32_t now = millis();
  if (now - lastAlarmCheck >= 200) {
    lastAlarmCheck = now;
    checkAlarm();
  }
  if (mode == RINGING && now - lastBeep >= 550) {
    lastBeep = now;
    beepPhase = !beepPhase;
    tone(BUZZER_PIN, beepPhase ? 2200 : 1650);
  }
  if (mode == NORMAL && now - lastUiDraw >= 1000) {
    lastUiDraw = now;
    drawUi();
  }
}
