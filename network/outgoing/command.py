# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structure
PacketCommand = Struct(
	"header"	/ PacketHeader,
	"value"		/ Default(PaddedString(16, "utf-8"), ""),
	"text"		/ Default(PaddedString(100, "utf-8"), "")
)

# Register packet
PacketHandler.register('Command', PacketCommand, 0x334)