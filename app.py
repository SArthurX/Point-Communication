import serial
import threading
import time

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
    # 通知類型
    NTF_BLE_TARGET_SCANNED = 0xA1
    NTF_UWB_RNG_DATA = 0xA2
    NTF_UWB_DISTANCE_ALERT = 0xA3

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
                response = self.m_serial.read_until()  # Read the entire response
                self.process_response(response)

    def process_response(self, data):
        if len(data) < 3:
            print("Received incomplete data.")
            return
        tlv_type = data[0]
        tlv_length = (data[1] << 8) | data[2]
        tlv_value = data[3:]

        # 解析不同類型的回傳值
        if tlv_type == TlvDefs.NTF_BLE_TARGET_SCANNED:
            print("BLE address:", tlv_value)
        elif tlv_type == TlvDefs.NTF_UWB_RNG_DATA:
            print("uwb rng data:", tlv_value)
        elif tlv_type == TlvDefs.NTF_UWB_DISTANCE_ALERT:
            print("uwb alert:", tlv_value)
        else:
            print("unknown tlv type:", tlv_type)

def main():
    # 初始化 serial 和 TLV builder
    port = "COM3" 
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
    tlv_builder.tlv_start(TlvDefs.TLV_TRACKER_CMD)
    tlv_builder.tlv_add_byte(TlvDefs.TRACKER_START_SCAN)
    tlv_builder.tlv_send(m_serial)
    time.sleep(10) 

    # 發送 TRACKER_STOP_SCAN 指令以停止 BLE 掃描
    tlv_builder.tlv_start(TlvDefs.TLV_TRACKER_CMD)
    tlv_builder.tlv_add_byte(TlvDefs.TRACKER_STOP_SCAN)
    tlv_builder.tlv_send(m_serial)

    # 發送 TRACKER_TRACK_DEVICE_START 指令以追蹤特定裝置
    tlv_builder.tlv_start(TlvDefs.TLV_TRACKER_CMD)
    tlv_builder.tlv_add_byte(TlvDefs.TRACKER_TRACK_DEVICE_START)
    mac_address = bytearray([0x01, 0x23, 0x45, 0x67, 0x89, 0xAB])  
    tlv_builder.tlv_add_data(mac_address)
    tlv_builder.tlv_send(m_serial)

    print("sent cmd done")

if __name__ == "__main__":
    main()
