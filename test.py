from serial_manager.simple_serial import SimpleSerial
from tlv.simple_tlv_builder import SimpleTlvBuilder
from tracker.tracker_controller import TrackerController

def main():
    port = "/dev/ttyUSB0"  # replace this with your port name
    serial_connection = SimpleSerial(port)
    serial_connection.open()

    tlv_builder = SimpleTlvBuilder(serial_connection)
    tracker_controller = TrackerController(serial_connection, tlv_builder)
    
    tracker_controller.start_tracking()
    
if __name__ == "__main__":
    main()
