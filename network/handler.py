# -*- coding: UTF-8 -*-
from network.packet import PacketBase

class PacketHandler:
	packet_list = []

	@classmethod
	def register(cls, name, struct, opcode, recv = False):
		cls.packet_list.append({
			"name": name,
			"recv": recv,
			"opcode": opcode,
			"struct": struct,
		})

	@classmethod
	def get_packet_by_opcode(cls, opcode, recv = False, size = None):
		for value in cls.packet_list:
			if opcode == value["opcode"] and recv == value["recv"] and (size is None or size == value['struct'].sizeof()):
				return value['name'], value['struct']
		return f"UNKNOWN_0x{opcode:X}", PacketBase

	@classmethod
	def get_packet_by_name(cls, name, recv = False, size = None):
		for value in cls.packet_list:
			if name == value["name"] and recv == value["recv"] and (size is None or size == value['struct'].sizeof()):
				return value["opcode"], value['struct']
		return 0, PacketBase
