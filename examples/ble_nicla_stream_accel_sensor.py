# SPDX-FileCopyrightText: 2020 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
Demonstration of a Bluefruit BLE Central for Circuit Playground Bluefruit. Connects to the first BLE
Nicla peripheral it finds. Sends Bluefruit ColorPackets, read from three accelerometer axis, to the
peripheral.
"""

import time
import struct

import busio
import digitalio


from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nicla import NiclaService



ble = BLERadio()

nicla_connection = None
# See if any existing connections are providing NiclaService.
if ble.connected:
    for connection in ble.connections:
        if NiclaService in connection:
            nicla_connection = connection
        break

SENS_ID_ACC = 4
#DEBUG = True
DEBUG = False
SCALE_DEFAULT_ACCEL = 4096.0

while True:
    if not nicla_connection:
        print("Scanning...")
        for adv in ble.start_scan(ProvideServicesAdvertisement, timeout=5):
            if NiclaService in adv.services:
                print("found a Nicla Sense ME device")
                nicla_connection = ble.connect(adv)
                break
        # Stop scanning whether or not we are connected.
        ble.stop_scan()

    sensorConfigured = False
    sensorDataPktCnt = 0
    while nicla_connection and nicla_connection.connected:
        try:
            if not sensorConfigured:
                st = struct.Struct("=BfI")
                sensorConfigPkt  = bytearray(9)
                st.pack_into(sensorConfigPkt, 0, SENS_ID_ACC, 1, 0)

                if DEBUG:
                    for b in sensorConfigPkt: print(hex(b))

                nicla_connection[NiclaService].write(sensorConfigPkt)
                sensorConfigured = True
                nicla_connection[NiclaService].write(sensorConfigPkt)
                print("sensor config packet sent for sensor accelerometer");

            sensorDataPkt = nicla_connection[NiclaService].read(34)
            sensorDataPktCnt += 1
            if DEBUG:
                print("new sensor data pkt ", sensorDataPktCnt);

            if (sensorDataPkt[0] == SENS_ID_ACC):
                if (sensorDataPkt[1] == 7):
                    buf = sensorDataPkt[0: 2 + 6]
                    (id, sz, x, y, z) = struct.unpack("=BBhhh", buf)
                    (X, Y, Z) = tuple(i / SCALE_DEFAULT_ACCEL for i in (x,y,z))

                    print("valid accelerometer data packet: #", sensorDataPktCnt, ",",  X, "," , Y, ",", Z)
                else:
                    print("invalid sensor data packet")

            else:
                    print("unrequested or unknown sensor data packet")

            if DEBUG:
                for b in sensorDataPkt: print(hex(b))

        except OSError:
            try:
                nicla_connection.disconnect()
                print("disconnected");
            except:  # pylint: disable=bare-except
                pass

            nicla_connection = None

        time.sleep(0.2)
