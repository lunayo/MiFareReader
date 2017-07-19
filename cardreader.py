#! /usr/bin/env python

from smartcard.System import readers

# define the APDUs used in this script
SELECT_MF = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
SELECT_EF = [0x00, 0xA4, 0x02, 0x00, 0x02, 0x00, 0x82]
READ = [0x00, 0xB0, 0x00, 0x00, 0x08]
# SELECT_EF = [0x00, 0xA4, 0x02, 0x00, 0x02, 0xEF, 0x01]

# get all the available readers
r = readers()
print "Available readers:", r

reader = r[1]
print "Using:", reader

connection = reader.createConnection()
connection.connect()

data, sw1, sw2 = connection.transmit(SELECT_MF)
print data

data, sw1, sw2 = connection.transmit(SELECT_EF)
print data

data, sw1, sw2 = connection.transmit(READ)
print data
print str.join("", ("%02x" % i for i in data))
