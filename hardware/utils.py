import os
import csv
from datetime import datetime


def get_mac_from_byte_array(value):
    """
    Utils method that converts a byte array to String MAC address
    :param value: Byte array of MAC address
    :return: String of MAC address
    """
    return (":".join('{:02x}'.format(i) for i in value)).upper()


def set_mac_to_byte_array(mac_input):
    """
    Utils method that converts a string MAC address to a byte array
    :param mac_input: String MAC address
    :return: bytearray of MAC address
    """
    mac = mac_input.split(":")
    result = bytearray()
    for field in mac:
        result += int(field, base=16).to_bytes(1, byteorder='big')

    return result


def get_string_from_byte_array(value):
    """
    Utils method that converts byte array to String
    :param value: Byte array of value
    :return: String of value
    """
    return value.decode().rstrip()


def get_int_from_byte_array(value):
    """
    Utils method that converts byte array to int16
    :param value: Byte array of value
    :return: int16 of value
    """
    return int.from_bytes(value, byteorder='big')


def get_time_stamp():
    """
    Utils method that gets time stamp in UTC format
    :return: String of time stamp in UTC format
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_aoa_value(aoa_value):
    if aoa_value > 90:
        aoa_value = aoa_value - 65536
    return aoa_value


def create_directory(name):
    if not os.path.exists(name):
        os.makedirs(name)

