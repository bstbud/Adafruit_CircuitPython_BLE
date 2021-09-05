# SPDX-FileCopyrightText: 2019 Dan Halbert for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
====================================================


"""

from . import Service
from ..uuid import VendorUUID
from ..characteristics.stream import StreamOut, StreamIn

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class NiclaService(Service):
    """
    :param int timeout:  the timeout in seconds to wait
      for the first character and between subsequent characters.
    :param int buffer_size: buffer up to this many bytes.
      If more bytes are received, older bytes will be discarded.

    See ``examples/ble_uart_echo_test.py`` for a usage example.
    """

    # pylint: disable=no-member
    uuid = VendorUUID("34C2E3BB-34AA-11EB-ADC1-0242AC120002")
    _server_tx = StreamOut(
        uuid=VendorUUID("34C2E3BC-34AA-11EB-ADC1-0242AC120002"),
        timeout=1.0,
        buffer_size=1024,
    )
    _server_rx = StreamIn(
        uuid=VendorUUID("34C2E3BD-34AA-11EB-ADC1-0242AC120002"),
        timeout=1.0,
        buffer_size=64,
    )

    def __init__(self, service=None):
        super().__init__(service=service)
        self.connectable = True
        if not service:
            self._rx = self._server_rx
            self._tx = self._server_tx
        else:
            # If we're a client then swap the characteristics we use.
            self._rx = self._server_tx
            self._tx = self._server_rx


    def read(self, nbytes=None):
        """
        Read characters. If ``nbytes`` is specified then read at most that many bytes.
        Otherwise, read everything that arrives until the connection times out.
        Providing the number of bytes expected is highly recommended because it will be faster.

        :return: Data read
        :rtype: bytes or None
        """
        return self._rx.read(nbytes)

    def readinto(self, buf, nbytes=None):
        """
        Read bytes into the ``buf``. If ``nbytes`` is specified then read at most
        that many bytes. Otherwise, read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)
        """
        return self._rx.readinto(buf, nbytes)

    @property
    def in_waiting(self):
        """The number of bytes in the input buffer, available to be read."""
        return self._rx.in_waiting

    def reset_input_buffer(self):
        """Discard any unread characters in the input buffer."""
        self._rx.reset_input_buffer()

    def write(self, buf):
        """Write a buffer of bytes."""
        self._tx.write(buf)

