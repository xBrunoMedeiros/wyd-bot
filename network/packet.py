# -*- coding: UTF-8 -*-	
from construct import *
from network.security import NetworkSecurity
# including encode latin-1
possiblestringencodings['latin1'] = 1

PacketHeader = Struct(
	"size"		/ Default(Int16ul, 12),
	"key"		/ Default(Int8ul, 0),
	"checksum"	/ Default(Int8ul, 0),
	"opcode"	/ Default(Int16ul, 0),
	"session"	/ Default(Int16ul, 0),
	"timestamp"	/ Default(Int32ul, 0),
)

PacketBase = Struct(
	"header"	/ PacketHeader,
	"content"	/ Bytes(this.header.size - PacketHeader.sizeof())
)

def generate_key(index, keys):
	''' Algorithm to generate the next key, using the client logic '''
	if index <= 15:
		return keys[index] ^ 0xFF
	elif keys[0xF] % 2:
		return (keys[0xB] + keys[0xD] - keys[0x9] + 4) ^ 0xFF
	else:
		return (keys[0x3] + keys[0x1] + keys[0x5] - 87) ^ 0xFF

def encrypt(data):
	# format data
	data = bytearray(data)
	# get header informations
	packet_size = len(data)
	packet_key = data[2] 
	# get data informations
	keyword = NetworkSecurity.Keys[0:][ 2 * ( packet_key & 0xFF ) ]
	sum1, sum2 = ( 0, 0 )
	# loop decode
	for i in range(4, packet_size):
		# sum calc 1
		sum1 += data[i]
		key_byte = NetworkSecurity.Keys[1:][ 2 * ( keyword & 0xFF ) ]
		# check flag index
		if (i & 0x03) == 0:
			data[i] = ( data[i] + ( key_byte << 0x01 ) ) & 0xFF
		elif (i & 0x03) == 1:
			data[i] = ( data[i] - ( key_byte >> 0x03 ) ) & 0xFF
		elif (i & 0x03) == 2:
			data[i] = ( data[i] + ( key_byte << 0x02 ) ) & 0xFF
		elif (i & 0x03) == 3:
			data[i] = ( data[i] - ( key_byte >> 0x05 ) ) & 0xFF
		# sum calc 2
		sum2 += data[i]
		# inc keyword
		keyword += 1
	# set checksum
	data[3] = ( sum2 - sum1 ) & 0xFF
	return bytes(data)

def decrypt(data):
	# format data
	data = bytearray(data)
	# get header informations
	packet_size = len(data)
	packet_key = data[2] 
	# get data informations
	keyword = NetworkSecurity.Keys[0:][ 2 * ( packet_key & 0xFF ) ]
	sum1, sum2 = ( 0, 0 )
	# loop decode
	for i in range(4, packet_size):
		# sum calc 1
		sum1 += data[i]
		key_byte = NetworkSecurity.Keys[1:][ 2 * ( keyword & 0xFF ) ]
		# check flag index
		if (i & 0x03) == 0:
			data[i] = ( data[i] - ( key_byte << 0x01 ) ) & 0xFF 
		elif (i & 0x03) == 1:
			data[i] = ( data[i] + ( key_byte >> 0x03 ) ) & 0xFF 
		elif (i & 0x03) == 2:
			data[i] = ( data[i] - ( key_byte << 0x02 ) ) & 0xFF 
		elif (i & 0x03) == 3:
			data[i] = ( data[i] + ( key_byte >> 0x05 ) ) & 0xFF 
		# sum calc 2
		sum2 += data[i]
		# inc keyword
		keyword += 1
	# check checksum
	return bytes(data) if data[3] == ( sum1 - sum2 ) & 0xFF else None
