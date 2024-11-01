class SimpleTlvBuilder:
    def __init__(self, serial_connection):
        self.serial_connection = serial_connection

    def build_tlv(self, command_type, value=None):
        tlv = bytearray([command_type, 0x00, len(value) if value else 0])
        if value:
            tlv.extend(value)
        return tlv

    def send_tlv(self, command_type, value=None):
        tlv = self.build_tlv(command_type, value)
        self.serial_connection.send(tlv)
        print(f"TLV已發送: {tlv}")
