#include <esp_now.h>
#include <WiFi.h>

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

#define CHANNEL 1


void configDeviceAP() {
  const char *SSID = "Slave_1";
  bool result = WiFi.softAP(SSID, "Slave_1_Password", CHANNEL, 0);
  if (!result) {
    Serial.println("AP Config failed.");
  } else {
    Serial.println("AP Config Success. Broadcasting with AP: " + String(SSID));
    Serial.print("AP CHANNEL "); Serial.println(WiFi.channel());
  }
}

void OnDataRecv(const uint8_t *mac_addr, const uint8_t *data, int data_len) {
  display.clearDisplay();
  char macStr[18];
  snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x",
           mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
  display.println("Last Packet Recv from"); display.print(macStr);display.setCursor(0, 30);
  display.println("Last Packet Recv Data"); display.println(*data);display.setCursor(0, 0);
  display.display();
  // display.drawRect(10, 10, 50, 20, SSD1306_WHITE);
  // display.display();
}

void setup() {
  Serial.begin(115200);
  //Set device in STA mode to begin with
  WiFi.mode(WIFI_AP);
  configDeviceAP();
 
  Serial.print("AP MAC: "); Serial.println(WiFi.softAPmacAddress());

  WiFi.disconnect();
  if (!esp_now_init() == ESP_OK) {
    Serial.println("ESPNow Init Fail");
  }


  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("SSD1306 initialization failed"));
    for(;;);
  }

  display.clearDisplay();
  display.setTextSize(1); 
  display.setTextColor(SSD1306_WHITE); 
  display.setCursor(0, 0);

  esp_now_register_recv_cb(OnDataRecv);
}



void loop() {

}
