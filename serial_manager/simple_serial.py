import serial

class SimpleSerial:
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connection = None

    def open(self):
        self.connection = serial.Serial(self.port, self.baudrate)
        print("串口已開啟")

    def send(self, data):
        if self.connection.is_open:
            self.connection.write(data)

    def receive(self, length=1):
        if self.connection.is_open:
            return self.connection.read(length)

    def close(self):
        if self.connection.is_open:
            self.connection.close()
            print("串口已關閉")
