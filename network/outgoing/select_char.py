# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structure
PacketSelectChar = Struct(
	"header" / PacketHeader,
	"index"	 / Int32ul,
	Padding(20)
)

# Register packet
PacketHandler.register('SelectChar', PacketSelectChar, 0x213)