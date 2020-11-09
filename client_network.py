# -*- coding: UTF-8 -*-
import time
import struct
import asyncio
from network.handler import PacketHandler
from network.packet import PacketHeader, encrypt, decrypt, generate_key
from network.incoming import *
from network.outgoing import *

class ClientNetwork(asyncio.Protocol):
	''' Socket to communication with GameServer. '''

	# GetTickCount API - ctypes.windll.winmm.timeGetTime
	get_tick_count = lambda self: int(round(time.time() * 1000)) & 0xFFFFFFFF
	
	def __init__(self, parent = None):
		''' Triggered when a connection is starting. '''
		# setup members
		self._parent = parent
		self._transport = None
		self._values = {
			'buffer recv': b"",
			'session index': 0,
			'session count': 0,
			'session keys': b"\x00" * 16,
			'session update': 0,
			'session server': 0
		}

	@property
	def is_connected(self):
		''' Determines whether [is connected] '''
		return self._transport and not self._transport.is_closing()

	@property
	def session_index(self):
		return self._values['session index']

	def set_session_timer(self, timer):
		self._values['session update'] = self.get_tick_count()
		self._values['session server'] = timer

	def set_session_index(self, session_index):
		self._values['session index'] = session_index

	def set_session_keys(self, value):
		self._values['session keys'] = value
		self._values['session count'] = 0

	def process_buffer(self, buffer):
		''' Process all packets in the buffer '''
		while len(buffer) >= 12:
			# next packet size
			next_packet_size = struct.unpack("H", buffer[:2])[0]
			# validate size of the next packet
			if next_packet_size > len(buffer): break
			# process next packet
			try:
				packet_raw = buffer[:next_packet_size]
				packet_raw = decrypt(packet_raw)
				packet_opcode = struct.unpack("H", packet_raw[4:6])[0]
				packet_name, packet_struct = PacketHandler.get_packet_by_opcode(packet_opcode, recv = True)
				packet_data = packet_struct.parse(packet_raw)
				# trigger callback
				self._parent.emit("recv_packet", self, packet_opcode, packet_name, packet_data)
			finally:
				buffer = buffer[next_packet_size:]
		# return remaining buffer, which cannot be processed yet
		return buffer
		
	def connection_made(self, transport):
		''' Triggered when a connection is made. '''
		self._transport = transport
		# sending handshake
		self._transport.write(b"\x11\xF3\x11\x1F")
		# trigger callback
		self._parent.emit("connected", self)
 
	def connection_lost(self, exc):
		''' Triggered when the connection is lost or closed. '''
		# trigger callback
		self._parent.emit("disconnected", self)
 
	def data_received(self, data):
		''' Triggered when some data is received. '''
		self._values['buffer recv'] = self.process_buffer(self._values['buffer recv'] + data)

	def write_data(self, data):
		''' Write some data bytes to the transport. '''
		if self.is_connected:
			self._transport.write(data)
			return len(data)

	def write_packet(self, packet_name, data = { }):
		''' Write packet in the buffer to be sent to the server '''
		# get packet structure
		opcode, packet = PacketHandler.get_packet_by_name(packet_name, recv = False)
		# update header
		data.update({
			"header": {
				"size": packet.sizeof(),
				"key": generate_key(
					self._values['session count'],
					self._values['session keys']
				),
				"opcode": opcode,
				"session": self.session_index,
				"timestamp": self.get_tick_count() - self._values['session update'] + self._values['session server']
			}
		})
		# create packet
		raw_bytes = packet.build(data)
		# encrypt packet
		raw_bytes = encrypt(raw_bytes)
		# increment packet count
		self._values['session count'] += 1
		# write to the buffer to be sent
		return self.write_data(raw_bytes)

	def close(self):
		''' Close the transport connection. '''
		if self.is_connected:
			self._transport.close()