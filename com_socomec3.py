#!/usr/bin/env python2.7

# -----
# Application created for Diris A10
# -----

import serial
import time
import sys
import binascii

# DIRIS A10 modbus table
# https://www.socomec.com/files/live/sites/systemsite/files/SCP/6_gestion_energie/diris/diris_a10/PRO_880108_DirisA10.html

reading = (51284, 51285, 51286, 51288, 51289, 51290, 51292, 51311) # (V1(V), V2, V3, I1(A), I2, I3, P(W), Ea+(Wh)). All in U16 format.
size_msg = 5 #4 digits for the readings of interest + 1

# header of the modbus message to send :
header = [0x05,0x03]
header_size = 4
count_header = 0

class diris:
	# configuration and opening of RS485 port :
	def __init__ (self, port):
		self.port = port
		self.fault_comms = False;

	#CRC processing ------------------------------------------------------------
	def generate_crc16_table(self):
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

	def crc_initialise(self):
		data_single = []
		data_2_crc = []
		for i in range(len(reading)):
			add = int(reading[i])
			crc =0
			add_H = add >>8
			add_L = add & 0x00ff
			crc_L = 0x00
			crc_H = 0x00
			data_single = [chr(int(header[0])),chr(int(header[1])),chr(int(add_H)),chr(int(add_L)),chr(int(0)),chr(int(size_msg))]
			data_2_crc.append(list(data_single))
		return data_2_crc

	def update_crc(self):
		# crc = 0xffff
		# crc_init = self.generate_crc16_table()
		data = self.crc_initialise()
		print data #comprises 8 lists each with 6 elements
		crc_H = []
		crc_L = []
		for list in data:
			for a in list:
				crc = 0xffff
				crc_init = self.generate_crc16_table()
				idx = crc_init[(crc ^ ord(a)) & 0xff]
				crc = ((crc >> 8) & 0xff) ^ idx
			crc_H.append(crc & ~((crc>>8)<<8))
			crc_L.append(crc>>8)
		return zip(crc_H,crc_L)

	def query_msg(self):
		tab = []
		tab = self.update_crc()
		#message to send -----------------------------------------------------------
		for i in range(len(reading)):
			add = int(reading[i])
			add_H = add >>8
			add_L = add & 0x00ff
			msg = bytearray([header[0],header[1],add_H,add_L,0,size_msg,tab[0][i],tab[1][i]])
			ser.write(msg)
			time.sleep(0.1)
			data_rec = ''
			count_size_msg =1
			while ser.inWaiting() > 0:
				rcv = ser.read(1)
				count_header+=1
				if count_header>header_size and count_size_msg<size_msg:
					count_size_msg+=1
					data_rec+=rcv
					data_hex = binascii.hexlify(data_rec)
				time.sleep(0.01)
		return data_hex
