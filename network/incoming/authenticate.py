# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structure
PacketAuthenticate = Struct(
	"header"	/ PacketHeader,
	"key_hash"	/ Bytes(16),
	"content"	/ Bytes(this.header.size - PacketHeader.sizeof() - 16)
)

# Register packet
PacketHandler.register('Authenticate', PacketAuthenticate, 0x10A, recv = True)