header = [0x05,0x03]
header_size =4
count_header = 0

# addess of register to read and size of the message expected
add = int(51284)
size_msg = int(2)+1

#initialization ------------------------------------------------------------
crc =0
add_H = add >>8
add_L = add & 0x00ff
crc_L = 0x00
crc_H = 0x00

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
print data_2_crc

def update_crc():
	crc = 0xffff
	data = data_2_crc
	for a in data:
		idx = crc_init[(crc ^ ord(a)) & 0xff]
		crc = ((crc >> 8) & 0xff) ^ idx
	crc_H = crc & ~((crc>>8)<<8)
	crc_L =  crc>>8
	return[crc_H,crc_L]

u = update_crc()
print u