#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

#define SCREEN_WIDTH 128 
#define SCREEN_HEIGHT 64 
#define OLED_RESET    -1 

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const char* ssid = your_ssid;
const char* password = your_password;


String serverUrl = your_server_ip;

void setup() {
  Serial.begin(115200);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  display.display();
  delay(2000); 

  display.clearDisplay();
 
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected");
}

void loop() {
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);

    int httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
      String payload = http.getString();
      Serial.println("HTTP Response: " + payload);

      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      }
      float angle = doc["angle"];
      String deviceName = doc["device_name"].as<String>();
      int distance = doc["distance"];

      Serial.println("Angle: " + String(angle));
      Serial.println("Device Name: " + deviceName);
      Serial.println("Distance: " + String(distance) + " cm");

      display.clearDisplay();
      display.setTextSize(1);
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 0);
      display.print("Dist: ");
      display.print(distance);
      display.print(" cm");

      display.setCursor(SCREEN_WIDTH - deviceName.length() * 6, 0); 
      display.print(deviceName);

      drawArrow(angle);

      display.display();
    } else {
      Serial.println("Error in HTTP request");
    }
    http.end();
  }
  delay(500);
}

void drawArrow(float angle) {
  int centerX = SCREEN_WIDTH / 2;
  int centerY = SCREEN_HEIGHT / 2;
  int length = 20; 

  float adjustedAngle = angle - 90; 

  float rad = adjustedAngle * PI / 180;
  int arrowX = centerX + length * cos(rad);
  int arrowY = centerY + length * sin(rad);

  display.drawLine(centerX, centerY, arrowX, arrowY, SSD1306_WHITE);
  display.drawCircle(centerX, centerY, 2, SSD1306_WHITE); 
}
