# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structure
PacketPincode = Struct(
	"header" / PacketHeader,
	"code"	 / Default(PaddedString(4, "utf8"), "0000"),
	Padding(16)
)

# Register packet
PacketHandler.register('Pincode', PacketPincode, 0xFDE)