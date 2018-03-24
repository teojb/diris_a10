#!/usr/bin/env python2.7

# -----
# Application created to test RS485 communication of SOCOMEC device
#
# Auteur : Cedric Fuster, CISCREA.
#        : Segolene Pommier, CISCREA.
# Creation date  : 22/04/2016
# Rev Application: 0.16.04.22

import serial
import time
import sys

args = []

for arg in sys.argv:
    args.append(arg)

if ((len(args)>1) and (args[1]== 'h')):
	print "--------------------------------------------------------------------"
	print "HELP :"
	print "This program enables to test the RS485 communication of SOCOMEC of the power case."
	print "It opens virual serial port (file /dev/VCom) and sets the baudrate at 9600 bauds."
	print "The program reads and writes data on this com port."
	print "The first argument is the decimal address of register to read, see <http://www.socomec.fr/files/live/sites/systemsite/files/SCP/6_gestion_energie/diris/diris_a10/PRO_880108_DirisA10.html>"
	print "The second argument is the size of the message to read"
	print ""
	print "TERMINAL COMMAND EXAMPLE:"
	print "sudo python com_socomec.py 50042 8"
	print "--------------------------------------------------------------------"

elif len(args)==3 and int(args[2])>0 and int(args[1])>=0 :
    # configuration and opening of RS485 port :
	ser = serial.Serial(port='/dev/Vcom', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
	ser.isOpen()

	# header of the modbus message to send :
	header = [0x05,0x03]
	header_size =4
	count_header = 0

	# addess of register to read and size of the message expected
	add = int(args[1])
	size_msg = int(args[2])+1

	#initialization ------------------------------------------------------------
	crc =0
	add_H = add >>8
	add_L = add & 0x00ff
	crc_L = 0x00
	crc_H = 0x00


	#CRC processing ------------------------------------------------------------
	def generate_crc16_table():
		result = []
		for byte in range(256):
			crc = 0x0000
			for _ in range(8):
				if (byte ^ crc) & 0x0001:
					crc = (crc >> 1) ^ 0xa001
				else: crc >>= 1
				byte >>= 1
			result.append(crc)
		return result

	crc_init = generate_crc16_table()
	data_2_crc = [chr(int(header[0])),chr(int(header[1])),chr(int(add_H)),chr(int(add_L)),chr(int(0)),chr(int(size_msg))]

	def update_crc():
		crc = 0xffff
		data = data_2_crc
		for a in data:
			idx = crc_init[(crc ^ ord(a)) & 0xff]
			crc = ((crc >> 8) & 0xff) ^ idx
		crc_H = crc & ~((crc>>8)<<8)
		crc_L =  crc>>8
		return[crc_H,crc_L]

	tab = []
	tab = update_crc()



	#message to send -----------------------------------------------------------
	msg = bytearray([header[0],header[1],add_H,add_L,0,size_msg,tab[0],tab[1]])

	# set mode RS485 transmit
	#ser.setDTR(0)
	#ser.setRTS(0)

	# send message
	ser.write( msg)

	# set mode RS485 receive
	time.sleep(0.1)
	#ser.setDTR(1)
	#ser.setRTS(1)
	data_rec = ''
	count_size_msg = 1
	#waiting for the answer

	while ser.inWaiting() > 0:
		rcv = ser.read(1)
		count_header+=1
		if count_header>header_size and count_size_msg<size_msg:
			count_size_msg+=1
			data_rec+=rcv
		time.sleep(0.01)

	#data received
	import binascii
	data_hex = binascii.hexlify(data_rec)
	#data_hex = data_rec.encode('hex')
	#print str(data_rec)
	# print int(binascii.hexlify(data_rec),16)
	data_dec32 = int(data_hex, 32)
	#print chr(int(data_hex))
	data_dec16 = int(data_hex, 16)
	#print ""
	print("Data Received : " + data_rec + ", hex: " + str(data_hex) + ", dec (int16):" + str(data_dec16) + ", dec (int32): " + str(data_dec32))
	#print ""

else:
	print 'wrong arguments'
	# print ""
	# print "Wrong arguments, 2 arguments needed, try 'sudo python com_socomec.py h' for help"
	# print ""
