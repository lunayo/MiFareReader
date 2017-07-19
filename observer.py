#! /usr/bin/env python
"""
Sample script that monitors smartcard insertion/removal.

__author__ = "http://www.gemalto.com"

Copyright 2001-2012 gemalto
Author: Jean-Daniel Aussel, mailto:jean-daniel.aussel@gemalto.com

This file is part of pyscard.

pyscard is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or
(at your option) any later version.

pyscard is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with pyscard; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

from sys import stdin, exc_info
from time import sleep

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import *
from smartcard.System import readers
import requests
import json
from apns import APNs, Payload

# define the APDUs used in this script
SELECT_MF = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
SELECT_EF = [0x00, 0xA4, 0x02, 0x00, 0x02, 0x00, 0x82]
READ = [0x00, 0xB0, 0x00, 0x00, 0x08]

# a simple card observer that prints inserted/removed cards
class printobserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def push_notification(self, message):
        apns = APNs(use_sandbox=True, cert_file='cert.pem', key_file='key.pem')

        # Send a notification
        token_hex = 'a5f8877b7c3126bfdbc58604a3a25f74bc573b44960fdb917559b1e3ce6f6cd1'
        payload = Payload(alert=message, sound="default", badge=1)
        apns.gateway_server.send_notification(token_hex, payload)

    def get_serial_number(self):
        r = readers()
        print "Available readers:", r

        reader = r[1]
        print "Using:", reader

        connection = reader.createConnection()
        connection.connect()

        data, sw1, sw2 = connection.transmit(SELECT_MF)
        data, sw1, sw2 = connection.transmit(SELECT_EF)
        data, sw1, sw2 = connection.transmit(READ)

        connection.disconnect()
        return str.join("", ("%02x" % i for i in data))

    def update(self, observable, (addedcards, removedcards)):
        for card in addedcards:
            print "+Inserted: ", toHexString(card.atr)
            serial_number = self.get_serial_number()
            print "Serial: ", serial_number
            # check in to the database
            url = "http://localhost:9000/activity/" + serial_number
            data = { "machineId" : 1}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=json.dumps(data), headers=headers)
            self.push_notification("Card number " + serial_number + " has checked in / out")
            print r

try:
    print "Insert or remove a smartcard in the system."
    print "This program will exit in 10 seconds"
    print ""
    cardmonitor = CardMonitor()
    cardobserver = printobserver()
    cardmonitor.addObserver(cardobserver)

    sleep(10000)

    # don't forget to remove observer, or the
    # monitor will poll forever...
    cardmonitor.deleteObserver(cardobserver)

    import sys
    if 'win32' == sys.platform:
        print 'press Enter to continue'
        sys.stdin.read(1)

except:
    print exc_info()[0], ':', exc_info()[1]