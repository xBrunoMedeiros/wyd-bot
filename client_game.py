# -*- coding: UTF-8 -*-
import pyee
import logging
import asyncio
import coloredlogs
from enum import Enum
from utils import MockTimeout
from models import dict2obj
from client_network import ClientNetwork

# Format colors in loggers
coloredlogs.DEFAULT_FIELD_STYLES['levelname']['color'] = 'yellow'
coloredlogs.install(level="DEBUG", fmt='[ %(asctime)s %(name)s ] %(levelname)s: %(message)s', datefmt='%d/%m/%y %H:%M:%S')

# Enum game stages
class ClientStage(Enum):
	DISCONNECTED, CONNECTING, AUTHENTICATING, UNLOCKING_PINCODE, SELECTING_CHARACTER, WORLD = range(6)

class ClientGame(pyee.EventEmitter):
	''' Clientless, able to simulate official client packets and connect to the game. '''

	def __init__(self, loop, server_address):
		''' Constructor '''
		# inheritance constructor
		pyee.EventEmitter.__init__(self)
		# logger configure
		self.logger = logging.getLogger(f"{id(self)}")
		self.logger.name = self
		# internal members
		self._loop = loop
		self._stage = ClientStage.DISCONNECTED
		self.network = None
		# default informations
		self._values = {
			"server address": server_address,
			"message": None,
			"username": None,
			"password": None,
			"objects": { }
		}
		# register handles of events
		self.on("connected", self.handle_connected)
		self.on("disconnected", self.handle_disconnected)
		self.on("recv_packet", self.handle_recv_packet)

	def __str__(self):
		''' Return a string representation of the class instance. '''
		return f"{self.__class__.__name__}<Index: {id(self):X}, Stage: {self._stage.name}, User: {self._values['username']}>"

	@property
	def last_message(self):
		''' Returns the last message received by the server '''
		return self._values['message']

	@property
	def objects(self):
		''' Returns list of all objects in the field of view '''
		if self._stage == ClientStage.WORLD:
			return self._values['objects']

	def get_object(self, index = None):
		''' Returns the object with the specified index '''
		object_index = index if index else self.network.session_index
		if object_index in self._values['objects']:
			return self._values['objects'][object_index]

	def get_stage(self):
		''' Get current instance stage '''
		return self._stage

	def set_stage(self, stage):
		''' Update instance stage '''
		self._stage = stage
		self.emit("update_stage", stage)

	async def authenticate(self, username, password, timeout = 3.0):
		''' Connect and authenticate to the server '''
		# check socket stage
		if self._stage == ClientStage.DISCONNECTED:
			# create intance of mock timeout
			mock = MockTimeout(return_value = None)
			try:
				# event: establishing connection
				self.set_stage(ClientStage.CONNECTING)
				# setup extra members
				self._values['message'] = None
				self._values['objects'] = { }
				# setup information to authentication 
				self._values['username'] = username
				self._values['password'] = password
				# start connection
				transport, self.network = await self._loop.create_connection(lambda: ClientNetwork(self), *self._values['server address'])
				# register event
				@self.on("update_stage")
				def handle_update_stage(stage):
					if stage == ClientStage.DISCONNECTED:
						mock.return_value = False
						mock()
					elif stage == ClientStage.UNLOCKING_PINCODE:
						mock.return_value = True
						mock()
				# send authenticate packet
				self.network.write_packet('Authenticate', {
					# account informations
					"password": self._values['username'],
					"username": self._values['password'],
					# required informations to fernando server
					"mac_address": "\x31\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32",
				})
				# mock event wait
				if not await mock.wait(timeout = timeout):
					# force disconnect
					self.network.close()
				# remove event
				self.remove_listener('update_stage', handle_update_stage)
			except (ConnectionRefusedError, TimeoutError) as error:
				self._values['message'] = "Connection Error"
				self.logger.error(f"Could not establish connection to the server: {self._server_address}")
				self.set_stage(ClientStage.DISCONNECTED)
			# return operation result
			return mock.return_value
		# the instance is busy, it needs to be disconnected to start a new connection.
		else:
			return False
	
	async def pincode(self, code, timeout = 3.0):
		''' Confirm pincode on server '''
		# check socket stage
		if self._stage == ClientStage.UNLOCKING_PINCODE:
			# create intance of mock timeout
			mock = MockTimeout(return_value = None)
			# register event
			@self.on("update_stage")
			def handle_update_stage(stage):
				if stage == ClientStage.DISCONNECTED:
					mock.return_value = False
					mock()
				elif stage == ClientStage.UNLOCKING_PINCODE:
					mock.return_value = False
					mock()
				elif stage == ClientStage.SELECTING_CHARACTER:
					mock.return_value = True
					mock()
			# send pincode request
			self.network.write_packet("Pincode", { "code": code })
			# mock event wait
			if not await mock.wait(timeout = timeout):
				# force disconnect
				self.network.close()
			# remove event
			self.remove_listener('update_stage', handle_update_stage)
			# return operation result
			return mock.return_value
		else:
			return False

	async def select_char(self, index, timeout = 3.0):
		''' Select character '''
		# check socket stage
		if self._stage == ClientStage.SELECTING_CHARACTER:
			# create intance of mock timeout
			mock = MockTimeout(return_value = None)
			# register event
			@self.on("update_stage")
			def handle_update_stage(stage):
				if stage == ClientStage.DISCONNECTED:
					mock.return_value = False
					mock()
				elif stage == ClientStage.WORLD:
					mock.return_value = True
					mock()
			# send select char request
			self.network.write_packet("SelectChar", { "index": index })
			# mock event wait
			if not await mock.wait(timeout = timeout):
				# force disconnect
				self.network.close()
			# remove event
			self.remove_listener('update_stage', handle_update_stage)
			# return operation result
			return mock.return_value
		else:
			return False

	def logout(self):
		''' Disconnect from server '''
		if self._stage.value >= ClientStage.AUTHENTICATING.value:
			self.network.close()

	def handle_connected(self, network):
		''' Handle called when socket is connected '''
		self.logger.debug("handle_connected")
		self.set_stage(ClientStage.AUTHENTICATING)

	def handle_disconnected(self, network):
		''' Handle called when socket is disconnected '''
		self.logger.debug("handle_disconnected")
		self.set_stage(ClientStage.DISCONNECTED)

	def handle_recv_packet(self, network, packet_opcode, packet_name, packet_data):
		''' Handle called when socket received packet '''
		if packet_name[:7] == 'UNKNOWN':
			self.logger.debug("recv_packet: { Size: %d, Session: %d, Name: '%s' }" % (packet_data.header.size, packet_data.header.session, packet_name))
		else:
			self.logger.debug("recv_packet: { Size: %d, Session: %d, Name: '%s' }" % (packet_data.header.size, packet_data.header.session, packet_name))
		# Update useful information to generate packet keys, packet timestamp and update stages.
		if packet_name == "Authenticate":
			self.network.set_session_timer(packet_data.header.timestamp)
			self.network.set_session_keys(packet_data.key_hash)
			self.set_stage(ClientStage.UNLOCKING_PINCODE)
		# Update stage warn that it failed, this can be removed with adaptations in function pincode.
		elif packet_name == "PincodeRefused":
			self.set_stage(ClientStage.UNLOCKING_PINCODE)
		# Update stage
		elif packet_name == "PincodeAccepted":
			self.set_stage(ClientStage.SELECTING_CHARACTER)
		# Update your own character's session index and information to generate packet timestamp.
		elif packet_name == "EnterWorld":
			self.network.set_session_timer(packet_data.header.timestamp)
			self.network.set_session_index(packet_data.session_index)
			self.set_stage(ClientStage.WORLD)
		# Include object in list
		elif packet_name == "CreateMob":
			self._values['objects'][packet_data.index] = dict2obj({
				'name': packet_data.name,
				'speed': packet_data.score.move.speed,
				'position': {
					'x': packet_data.position.x,
					'y': packet_data.position.y
				}
			})
		# Delete object that left the field of view.
		elif packet_data == "DeleteMob":
			self._values['objects'].pop(packet_data.header.session)
		# Update object position.
		elif packet_name == "Movement":
			self._values['objects'][packet_data.header.session].position.x = packet_data.destiny.x
			self._values['objects'][packet_data.header.session].position.y = packet_data.destiny.y
		# Update last message received from the server.
		elif packet_name == "ServerMessage":
			self._values['message'] = packet_data.text
		# TODO: This should not update every packet, this was a temporary solution that i found.
		self.network.set_session_timer(packet_data.header.timestamp)
