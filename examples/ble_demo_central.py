"""
Demonstration of a Bluefruit BLE Central. Connects to the first BLE UART peripheral it finds.
Sends Bluefruit ColorPackets, read from three potentiometers, to the peripheral.
"""

import time

import board
from analogio import AnalogIn

#from adafruit_bluefruit_connect.packet import Packet
# Only the packet classes that are imported will be known to Packet.
from adafruit_bluefruit_connect.color_packet import ColorPacket

from adafruit_ble.scanner import Scanner
from adafruit_ble.uart_client import UARTClient

def scale(value):
    """Scale an value from 0-65535 (AnalogIn range) to 0-255 (RGB range)"""
    return int(value / 65535 * 255)

scanner = Scanner()
uart_client = UARTClient()
uart_addresses = []

# Keep trying to find a UART peripheral
while not uart_addresses:
    uart_addresses = uart_client.scan(scanner)

a0 = AnalogIn(board.A0)
a1 = AnalogIn(board.A1)
a2 = AnalogIn(board.A2)

while True:
    uart_client.connect(uart_addresses[0], 5)
    while uart_client.connected:
        r = scale(a0.value)
        g = scale(a1.value)
        b = scale(a2.value)

        color = (r, g, b)
        print(color)
        color_packet = ColorPacket(color)
        try:
            uart_client.write(color_packet.to_bytes())
        except OSError:
            pass
        time.sleep(0.3)
