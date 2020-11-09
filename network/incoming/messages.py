# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structures
PacketMessage = Struct(
	"header"	/ PacketHeader,
	"text"		/ FixedSized(96, CString("latin1"))
)

PacketMessageWhisper = Struct(
	"header"	/ PacketHeader,
	"cmd"		/ FixedSized(16, CString("latin1")),
	"text"		/ FixedSized(100, CString("latin1"))
)

# Register packets - Incoming
PacketHandler.register('ServerMessage', PacketMessage, 0x101, recv = True)
PacketHandler.register('ChatMessage', PacketMessage, 0x333, recv = True)
PacketHandler.register('ChatWhisper', PacketMessageWhisper, 0x334, recv = True)

# Register packets - Outgoing
# ...