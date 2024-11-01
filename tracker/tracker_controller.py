import threading

class TrackerController:
    def __init__(self, serial_connection, tlv_builder):
        self.serial_connection = serial_connection
        self.tlv_builder = tlv_builder
        self.active = True

    def start_tracking(self):
        # 發送BLE掃描指令
        self.tlv_builder.send_command(command_type=0x20)  # 假設0x20為啟動掃描指令

        tracking_thread = threading.Thread(target=self.receive_data)
        tracking_thread.start()

    def stop_tracking(self):
        # 停止追蹤的指令
        self.tlv_builder.send_command(command_type=0x21)  # 假設0x21為停止指令
        self.active = False

    def receive_data(self):
        while self.active:
            data = self.serial_connection.receive(10)  # 假設每次接收10字節
            if data:
                self.parse_data(data)

    def parse_data(self, data):
        distance = int.from_bytes(data[1:3], byteorder='big')  # 距離解析
        angle = int.from_bytes(data[3:5], byteorder='big', signed=True)  # 角度解析
        print(f"接收到數據 - 距離: {distance}, 角度: {angle}")
