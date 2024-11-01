class SimpleTlvBuilder:
    def __init__(self, serial_connection):
        self.serial_connection = serial_connection

    def send_command(self, command_type, payload=None):
        tlv = bytearray([command_type, 0x00, len(payload) if payload else 0])
        if payload:
            tlv.extend(payload)
        self.serial_connection.send(tlv)
        print(f"指令發送: {tlv}")
