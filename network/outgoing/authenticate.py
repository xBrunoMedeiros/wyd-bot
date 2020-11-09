# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

'''
# Create packet structure
PacketAuthenticate = Struct(
	"header"			/ PacketHeader,
	"password"			/ Default(PaddedString(12, "utf8"), ""),
	"username"			/ Default(PaddedString(12, "utf8"), ""),
	"serial"			/ Default(FixedSized(30, CString("latin1")), ""), 
	"mac_address"		/ Default(FixedSized(18, CString("latin1")), ""),
	"client_version"	/ Default(Int16ul, 1),
	Padding(6),
	"game_version"		/ Default(Int16ul, 7556),
	Padding(2),
	"client_state"		/ Default(Int16ul, 1),
	Padding(2),
	"unique_key"		/ Default(FixedSized(16, CString("latin1")), "")
)
'''
# Fernando Server
PacketAuthenticate = Struct(
	"header"			/ PacketHeader,
	"username"			/ Default(PaddedString(12, "latin1"), ""),
	"password"			/ Default(PaddedString(12, "latin1"), ""),
	"mac_address"		/ Default(PaddedString(18, "latin1"), ""),
	"serial"			/ Default(PaddedString(30, "latin1"), ""),
	"client_version"	/ Default(Int16ul, 1),
	Padding(6),
	"game_version"		/ Default(Int16ul, 1905),
	Padding(2),
	"client_state"		/ Default(Int16ul, 12),
	Padding(2),
	"unique_key"		/ Default(PaddedString(16, "latin1"), "")
)
'''
# UltimateLegends Server
PacketAuthenticate = Struct(
	"header"			/ PacketHeader,
	"username"			/ Default(PaddedString(12, "latin1"), ""),
	"password"			/ Default(PaddedString(12, "latin1"), ""),
	"mac_address"		/ Default(PaddedString(20, "latin1"), ""),
	Padding(28),
	"client_version"	/ Default(Int16ul, 1603),
	"shield"			/ Default(Int16ul, 150),
	Padding(4),
	"game_version"		/ Default(Int16ul, 1921),
	Padding(2),
	"client_state"		/ Default(Int16ul, 1),
	Padding(2),
	"unique_key"		/ Default(PaddedString(16, "latin1"), "")
)
'''
# Register packet
PacketHandler.register('Authenticate', PacketAuthenticate, 0x20D)