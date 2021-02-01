#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2011-2013 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
"""
Crazyflie USB driver.

This driver is used to communicate with the Crazyflie using the USB connection.
"""
import logging
import queue
import re
import threading

from .crtpstack import CRTPPacket
from .exceptions import WrongUriType
from cflib.crtp.crtpdriver import CRTPDriver
import nativelink

__author__ = 'Bitcraze AB'
__all__ = ['NativeDriver']

logger = logging.getLogger(__name__)


class NativeDriver(CRTPDriver):
    """ Crazyradio link driver """

    def __init__(self):
        """Driver constructor. Throw an exception if the driver is unable to
        open the URI
        """
        self.needs_resending = True

        self._connection = None

    def connect(self, uri, link_quality_callback, link_error_callback):
        """Connect the driver to a specified URI

        @param uri Uri of the link to open
        @param link_quality_callback Callback to report link quality in percent
        @param link_error_callback Callback to report errors (will result in
               disconnection)
        """

        self._connection = nativelink.Connection(uri)

    def send_packet(self, pk):
        """Send a CRTP packet"""
        nativePk = nativelink.Packet()
        nativePk.port = pk.port
        nativePk.channel = pk.channel
        nativePk.size = len(pk.data)
        nativePk.payload = bytes(pk.data)

        self._connection.send(nativePk)

    def receive_packet(self, wait=0):
        """Receive a CRTP packet.

        @param wait The time to wait for a packet in second. -1 means forever

        @return One CRTP packet or None if no packet has been received.
        """
        forever = False
        if wait < 0:
            wait = 0.1
            forever = True

        while True:
            nativePk = self._connection.recv(timeout=int(wait*1000))

            if (not nativePk.valid) and forever:
                continue

            if not nativePk.valid:
                return None

            pk = CRTPPacket()
            pk.port = nativePk.port
            pk.channel = nativePk.channel
            pk.data = nativePk.payload

            return pk


    def get_status(self):
        """
        Return a status string from the interface.
        """
        "okay"

    def get_name(self):
        """
        Return a human readable name of the interface.
        """
        "NativeLink"

    def scan_interface(self, address=None):
        """
        Scan interface for available Crazyflie quadcopters and return a list
        with them.
        """
        scan = nativelink.Connection.scan('')
        resp = []

        for found in scan:
            resp.append([found, ''])

        print(resp)
        return resp

    def enum(self):
        """Enumerate, and return a list, of the available link URI on this
        system
        """
        return self.scan_interface()

    def get_help(self):
        """return the help message on how to form the URI for this driver
        None means no help
        """
        ""

    def close(self):
        """Close the link"""
        self._connection.close()
        self._connection = None
