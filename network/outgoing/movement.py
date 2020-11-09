# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create position structure
Position = Struct(
	"x"	/ Int16ul,
	"y"	/ Int16ul
)

# Create packet structure
PacketMovement = Struct(
	"header"	/ PacketHeader,
	"source"	/ Position,
	"type"		/ Default(Int32ul, 0),
	"speed"		/ Default(Int32ul, 3),
	"command"	/ Default(FixedSized(24, CString("latin1")), ""),
	"destiny"	/ Position
)

# Create packet structure ( Bypass )
PacketMovementBypass = Struct(
	"header"	/ PacketHeader,
	"source"	/ Default(Position, {
		"x": 350,
		"y": 0,
	})
)

# Register packet
PacketHandler.register('MovementBypass', PacketMovementBypass, 0x36C)
PacketHandler.register('Movement', PacketMovement, 0x36C)