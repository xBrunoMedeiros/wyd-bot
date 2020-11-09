# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create packet structure
PacketPincode = Struct(
	"header" / PacketHeader
)

# Register packet
PacketHandler.register('PincodeAccepted', PacketPincode, 0xFDE, recv = True)
PacketHandler.register('PincodeRefused', PacketPincode, 0xFDF, recv = True)