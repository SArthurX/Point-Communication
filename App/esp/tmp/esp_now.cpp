#include <WiFi.h>

#include <esp_now.h>
#include <esp_wifi.h>

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

esp_now_peer_info_t slave;

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

#define CHANNEL 1

void ScanForSlave() {
  int16_t scanResults = WiFi.scanNetworks(false, false, false, 300, CHANNEL); 

    bool slaveFound = 0;
    memset(&slave, 0, sizeof(slave));

    Serial.println("");
    if (scanResults == 0) {
    Serial.println("No WiFi devices in AP Mode found");
    } else {
    Serial.print("Found ");
    Serial.print(scanResults);
    Serial.println(" devices ");
    for (int i = 0; i < scanResults; ++i) {
      // Print SSID and RSSI for each device found
        String SSID = WiFi.SSID(i);
        int32_t RSSI = WiFi.RSSI(i);
        String BSSIDstr = WiFi.BSSIDstr(i);

        if (0) {
            Serial.print(i + 1);
            Serial.print(": ");
            Serial.print(SSID);
            Serial.print(" (");
            Serial.print(RSSI);
            Serial.print(")");
            Serial.println("");
        }
        delay(10);
      // Check if the current device starts with `Slave`
        if (SSID.indexOf("Slave") == 0) {
        // SSID of interest
            Serial.println("Found a Slave.");
            Serial.print(i + 1);
            Serial.print(": ");
            Serial.print(SSID);
            Serial.print(" [");
            Serial.print(BSSIDstr);
            Serial.print("]");
            Serial.print(" (");
            Serial.print(RSSI);
            Serial.print(")");
            Serial.println("");
        // Get BSSID => Mac Address of the Slave
            int mac[6];
            if (6 == sscanf(BSSIDstr.c_str(), "%x:%x:%x:%x:%x:%x", &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5])) {
                for (int ii = 0; ii < 6; ++ii) {
                slave.peer_addr[ii] = (uint8_t)mac[ii];
                }
        }

        slave.channel = CHANNEL;  // pick a channel
        slave.encrypt = 0;        // no encryption

        slaveFound = 1;
        // we are planning to have only one slave in this example;
        // Hence, break after we find one, to be a bit efficient
        break;
        }
    }
}

    if (slaveFound) {
        Serial.println("Slave Found, processing..");
    } else {
        Serial.println("Slave Not Found, trying again.");
    }

    WiFi.scanDelete();
}

bool manageSlave() {
    if (slave.channel == CHANNEL) {
    // if (DELETEBEFOREPAIR) {
    //   deletePeer();
    // }

    // Serial.print("Slave Status: ");
    bool exists = esp_now_is_peer_exist(slave.peer_addr);
    if (exists) {
      // Slave already paired.
      // Serial.println("Already Paired");
        return true;
    } else {
        esp_err_t addStatus = esp_now_add_peer(&slave);
        if (addStatus == ESP_OK) {
        // Pair success
            Serial.println("Pair success");
            return true;
        } else if (addStatus == ESP_ERR_ESPNOW_NOT_INIT) {
            Serial.println("ESPNOW Not Init");
            return false;
        } else if (addStatus == ESP_ERR_ESPNOW_ARG) {
        Serial.println("Invalid Argument");
        return false;
        } else if (addStatus == ESP_ERR_ESPNOW_FULL) {
        Serial.println("Peer list full");
        return false;
        } else if (addStatus == ESP_ERR_ESPNOW_NO_MEM) {
        Serial.println("Out of memory");
        return false;
        } else if (addStatus == ESP_ERR_ESPNOW_EXIST) {
        Serial.println("Peer Exists");
        return true;
        } else {
        Serial.println("Not sure what happened");
        return false;
        }
    }
    } else {
    Serial.println("No Slave found to process");
    return false;
    }
}

void deletePeer() {
    esp_err_t delStatus = esp_now_del_peer(slave.peer_addr);
    Serial.print("Slave Delete Status: ");
    if (delStatus == ESP_OK) {
        Serial.println("Success");
    } else if (delStatus == ESP_ERR_ESPNOW_NOT_INIT) {
        Serial.println("ESPNOW Not Init");
    } else if (delStatus == ESP_ERR_ESPNOW_ARG) {
        Serial.println("Invalid Argument");
    } else if (delStatus == ESP_ERR_ESPNOW_NOT_FOUND) {
        Serial.println("Peer not found.");
    } else {
        Serial.println("Not sure what happened");
    }
}

String inputText;
void sendData() {
    if (Serial.available()) {
    inputText = Serial.readStringUntil('\n');  
    const uint8_t *peer_addr = slave.peer_addr;
    Serial.print("Sending: ");
    Serial.println(inputText);
    esp_err_t result = esp_now_send(peer_addr, (const uint8_t *)inputText.c_str(), inputText.length());
    Serial.print("Send Status: ");
    if (result == ESP_OK) {
        Serial.println("Success");
    } else {
        Serial.println("Failed");
    }
    }
}

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    char macStr[18];
    snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x",
             mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
    Serial.print("Last Packet Sent to: ");
    Serial.println(macStr);
    Serial.print("Last Packet Send Status: ");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}


void OnDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int data_len) {
 const uint8_t *mac_addr = info->src_addr;
    display.clearDisplay();
    char macStr[18];
    snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x",
             mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
    display.println("Last Packet Recv from");
    display.print(macStr);
    display.setCursor(0, 30);
    display.println("Last Packet Recv Data");
    
    String receivedData = "";
    for (int i = 0; i < data_len; i++) {
        receivedData += (char)data[i];
    }
    Serial.println(receivedData);
    display.println(receivedData);
    display.setCursor(0, 0);
    display.display();
}

void configDeviceAP() {
    const char *SSID = "Slave_b";
    bool result = WiFi.softAP(SSID, "00000000", CHANNEL, 0);
    if (!result) {
        Serial.println("AP Config failed.");
    } else {
        Serial.println("AP Config Success. Broadcasting with AP: " + String(SSID));
    }
}

void setup() {
    Serial.begin(115200);
    
    WiFi.mode(WIFI_AP_STA);
    esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);
    configDeviceAP();
    
    Serial.print("STA MAC: ");Serial.println(WiFi.macAddress()); //m
    Serial.print("STA CHANNEL ");Serial.println(WiFi.channel()); 
    Serial.print("AP MAC: "); Serial.println(WiFi.softAPmacAddress()); //s
    
    WiFi.disconnect();
    if (!esp_now_init() == ESP_OK) {
        Serial.println("ESPNow Init Fail");
    }
    
    if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
        Serial.println(F("SSD1306 initialization failed"));
    }
    
    display.clearDisplay();
    display.setTextSize(1); 
    display.setTextColor(SSD1306_WHITE); 
    display.setCursor(0, 0);
    display.println("test");
    
    esp_now_register_recv_cb(OnDataRecv);
    esp_now_register_send_cb(OnDataSent);
    
    ScanForSlave();
}

void loop() {
    if (slave.channel == CHANNEL) { 
        bool isPaired = manageSlave();
        if (isPaired) {
            sendData();
        } else {
        Serial.println("Slave pair failed!");
        }
        } else {
    }
    delay(250);
}
