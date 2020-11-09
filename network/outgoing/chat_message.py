# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structure
PacketChatMessage = Struct(
	"header"	/ PacketHeader,
	"text"		/ PaddedString(100, "latin1")
)

# Register packet
PacketHandler.register('ChatMessage', PacketChatMessage, 0x333)