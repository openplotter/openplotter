#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by sailoog <https://github.com/sailoog/openplotter>
#                     e-sailing <https://github.com/e-sailing/openplotter>
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import serial
import socket
import sys
from classes.conf import Conf
from classes.SK_settings import SK_settings

conf = Conf()

activ = False
activ = conf.get('N2K', 'output') == '1'
if not activ: sys.exit(0)

SK_settings = SK_settings(conf)

baudrate = SK_settings.ngt1_baudrate
can_device = SK_settings.ngt1_device
if baudrate and can_device:
	try:
		ser = serial.Serial(can_device, baudrate, timeout=0.5)
	except:
		print('failed to start N2K output server on '+can_device)
		sys.exit(0)
else: sys.exit(0)


Quelle = '127.0.0.1'  # Adresse des eigenen Rechners
Port = 55560

e_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # s.o.
e_udp_sock.bind((Quelle, Port))


def SendCommandtoSerial(TXs):
	crc = 0
	i = 0
	while i < TXs[1] + 2:
		crc += TXs[i]
		i += 1
	crc = (256 - crc) & 255
	TXs[TXs[1] + 2] = crc

	TYs = b''
	while i < TXs[1] + 3:
		TYs = TYs+bytes(TXs[i])
		if TXs[i] == 0x10:
			TYs = TYs+bytes(TXs[i])
		i += 1		
	start = b'\x10\x02'
	ende = b'\x10\x03'
	ser.write(start+TXs+ende)
	#print(start+TXs+ende)

def put_recive_to_serial():
	while 1:
		data1, addr = e_udp_sock.recvfrom(512)
		# Data buffer had to be potenz of 2
		data = bytearray(data1)
		data = data1
		if data[7] + 9 == len(data):
			SendCommandtoSerial(bytearray(data))
			#datap = ''
			#dat = 0
			#for i in range(8, data[7] + 9):
			#	dat = dat + data[i]
			#	datap += ' ' + ('0' + hex(data[i])[2:])[-2:]
			#print(datap)

put_recive_to_serial()
