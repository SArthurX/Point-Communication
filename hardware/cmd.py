import serial
import threading
import time
from flask import Flask, jsonify
from utils import *


app = Flask(__name__)

latest_uwb_data = {}


TRACKER_RNG_NTF_MSG = "[{}] {} {:>9} {:>4} cm {:>3}º"

class SerialDefs:
    SERIAL_MAX_BUFFER = 64  # 設定序列埠緩衝區大小

class TlvDefs:
    TLV_TRACKER_CMD = 0x02
    TRACKER_START_SCAN = 0x20
    TRACKER_STOP_SCAN = 0x21
    TRACKER_TRACK_DEVICE_START = 0x22
    APP_TRACKER = 0x2
    TLV_APP_CMD = 0x01
    APP_START = 0x10
    APP_STOP = 0x11
    # 通知類型
    NTF_BLE_TARGET_SCANNED = 0xA1
    NTF_UWB_RNG_DATA = 0xA2
    NTF_UWB_DISTANCE_ALERT = 0xA3
    TLV_NTF = 0x0A

class TlvBuilder:
    def __init__(self):
        self.m_tlv = None

    def tlv_start(self, tlv_type):
        self.m_tlv = type('', (), {})() 
        self.m_tlv.tlv_type = tlv_type
        self.m_tlv.tlv_value = bytearray()
        self.m_tlv.tlv_length = 0

    def tlv_add_byte(self, byte):
        self.m_tlv.tlv_value.append(byte)
        self.m_tlv.tlv_length += 1

    def tlv_add_data(self, data):
        self.m_tlv.tlv_value.extend(data)
        self.m_tlv.tlv_length += len(data)

    def tlv_send(self, m_serial):
        data = bytearray()
        data.append(self.m_tlv.tlv_type)
        data.append((self.m_tlv.tlv_length >> 8) & 0xff)
        data.append(self.m_tlv.tlv_length & 0xff)
        data += self.m_tlv.tlv_value
        m_serial.send(data)

class MSerial(threading.Thread):
    def __init__(self, port):
        super().__init__()
        self.m_serial = serial.Serial(port, baudrate=115200, timeout=1)
        self.active = True

    def send(self, data):
        num_chunks = self.calculate_number_of_chunks(data)
        for i in range(num_chunks):
            try:
                if i == (num_chunks - 1):
                    self.m_serial.write(data[i * SerialDefs.SERIAL_MAX_BUFFER:])
                else:
                    self.m_serial.write(data[i * SerialDefs.SERIAL_MAX_BUFFER:SerialDefs.SERIAL_MAX_BUFFER * (i + 1)])
            except serial.SerialException:
                print("Serial communication error.")

    def calculate_number_of_chunks(self, data):
        return (len(data) + SerialDefs.SERIAL_MAX_BUFFER - 1) // SerialDefs.SERIAL_MAX_BUFFER

    def run(self):
        while self.active:
            if self.m_serial.in_waiting > 0:
                response = self.m_serial.read_until() 
                self.process_response(response)



    def process_response(self, data):
            global latest_uwb_data 
            if len(data) < 3:
                print("Received incomplete data.")
                return
            
            tlv_type = data[0]
            tlv_length = (data[1] << 8) | data[2]
            tlv_value = data[3:]
            
            ble_mac = get_mac_from_byte_array(tlv_value[0:6])
            ble_short_name = get_string_from_byte_array(tlv_value[6:15])
            distance = get_int_from_byte_array(tlv_value[15:17])
            aoa = parse_aoa_value(get_int_from_byte_array(tlv_value[17:19]))
            time_stamp = get_time_stamp()
            print(TRACKER_RNG_NTF_MSG.format(time_stamp, ble_mac, ble_short_name, distance, aoa))

            # 更新最新的 UWB 資料
            latest_uwb_data = {
                "mac_address": ble_mac,
                "device_name": ble_short_name,
                "distance": distance,
                "angle": aoa,
                "timestamp": time_stamp
            }
        # 解析不同類型的回傳值
        # if tlv_type == TlvDefs.NTF_BLE_TARGET_SCANNED:
        #     # 使用工具函數解析 BLE MAC 地址和裝置名稱
        #     ble_mac = get_mac_from_byte_array(tlv_value[0:6])
        #     ble_short_name = get_string_from_byte_array(tlv_value[6:15])
        #     print(f"BLE Scanned Device - MAC: {ble_mac}, Name: {ble_short_name}")
        
        # elif tlv_type == TlvDefs.NTF_UWB_RNG_DATA:
        #     # 解析 UWB 距離數據，包括 MAC 地址、名稱、距離和角度
        #     ble_mac = get_mac_from_byte_array(tlv_value[0:6])
        #     ble_short_name = get_string_from_byte_array(tlv_value[6:15])
        #     distance = get_int_from_byte_array(tlv_value[15:17])
        #     aoa = parse_aoa_value(get_int_from_byte_array(tlv_value[17:]))
        #     time_stamp = get_time_stamp()
        #     print(f"UWB Ranging Data - Timestamp: {time_stamp}, MAC: {ble_mac}, Name: {ble_short_name}, "
        #         f"Distance: {distance}, AoA: {aoa}")
        
        # elif tlv_type == TlvDefs.NTF_UWB_DISTANCE_ALERT:
        #     # 解析 UWB 距離警報數據
        #     ble_mac = get_mac_from_byte_array(tlv_value[0:6])
        #     ble_short_name = get_string_from_byte_array(tlv_value[6:15])
        #     distance = get_int_from_byte_array(tlv_value[15:17])
        #     distance_threshold = tlv_value[17]
        #     time_stamp = get_time_stamp()
        #     print(f"UWB Distance Alert - Timestamp: {time_stamp}, MAC: {ble_mac}, Name: {ble_short_name}, "
        #         f"Distance: {distance}, Threshold: {distance_threshold}")
        
        # else:
        #     print("Unknown TLV type:", tlv_type)

@app.route('/getAngle', methods=['GET'])
def get_data():
    """API 路由：提供最新的 UWB 資訊"""
    global latest_uwb_data
    if latest_uwb_data:
        return jsonify(latest_uwb_data)
    else:
        return jsonify({"message": "No data available"}), 404
    
@app.route('/', methods=['GET'])
def home():
    """API 首頁路由：顯示簡單的歡迎訊息"""
    return jsonify({
        "message": "歡迎使用 UWB 資料 API！",
        "endpoints": {
            "/getAngle": "取得最新的 UWB 資訊"
        },
        "description": "使用此 API 來檢索最新的超寬頻 (UWB) 裝置追蹤資料。"
    })


if __name__ == "__main__":
    try:
        # 初始化 serial 和 TLV builder
        port = "/dev/tty.usbserial-D30A2TJB" 
        m_serial = MSerial(port)
        m_serial.start() 
        tlv_builder = TlvBuilder()

        # 發送 APP_START 指令以啟動追蹤應用
        tlv_builder.tlv_start(TlvDefs.TLV_APP_CMD)
        tlv_builder.tlv_add_byte(TlvDefs.APP_START)
        tlv_builder.tlv_add_byte(TlvDefs.APP_TRACKER)
        tlv_builder.tlv_send(m_serial)
        time.sleep(1)

        # 發送 TRACKER_START_SCAN 指令以開始 BLE 掃描
        # tlv_builder.tlv_start(TlvDefs.TLV_TRACKER_CMD)
        # tlv_builder.tlv_add_byte(TlvDefs.TRACKER_START_SCAN)
        # tlv_builder.tlv_send(m_serial)
        # time.sleep(10) 

        # # 發送 TRACKER_STOP_SCAN 指令以停止 BLE 掃描
        # tlv_builder.tlv_start(TlvDefs.TLV_TRACKER_CMD)
        # tlv_builder.tlv_add_byte(TlvDefs.TRACKER_STOP_SCAN)
        # tlv_builder.tlv_send(m_serial)

        # 發送 TRACKER_TRACK_DEVICE_START 指令以追蹤特定裝置
        tlv_builder.tlv_start(TlvDefs.TLV_TRACKER_CMD)
        tlv_builder.tlv_add_byte(TlvDefs.TRACKER_TRACK_DEVICE_START)
        mac_address = bytearray([0x00, 0x60, 0x37, 0x76, 0xB0, 0xEF])  
        tlv_builder.tlv_add_data(mac_address)
        tlv_builder.tlv_send(m_serial)

        print("sent cmd done")
        
        app.run(host="0.0.0.0" ,port="5005" ,use_reloader=False ,debug=True)

    except KeyboardInterrupt:
            print("Shutting down gracefully...")
            tlv_builder.tlv_start(TlvDefs.TLV_APP_CMD)
            tlv_builder.tlv_add_byte(TlvDefs.APP_STOP)
            tlv_builder.tlv_send(m_serial)
            m_serial.active = False  
            m_serial.join()  
            print("Exited safely.")

