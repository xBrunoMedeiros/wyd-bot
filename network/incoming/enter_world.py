# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structure
PacketEnterWorld = Struct(
	"header"			/ PacketHeader,
	Padding(0x2F8),
	"char_index"		/ Int16ul,
	"session_index"		/ Int16ul
)

# Register packet
PacketHandler.register('EnterWorld', PacketEnterWorld, 0x114, recv = True)