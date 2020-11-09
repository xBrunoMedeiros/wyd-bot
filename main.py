# -*- coding: UTF-8 -*-
import sys
# disable binarys
sys.dont_write_bytecode=True
# internal imports
import time
import asyncio
import asyncore
from client_game import ClientStage, ClientGame

async def flood_message(loop, username, password, pincode):
	# Server / channel address
	# server_address = ('127.0.0.1', 8281) # Own proxy
	# server_address = ('149.56.164.122', 8281) # Unknown
	# server_address = ('192.254.66.66', 8281) # Fernando VPS: Game
	server_address = ('51.81.111.61', 8281) # Fernando VPS: Website
	# ('149.56.164.122', 8281) # Ultimate Legends
	# Create clientless instance
	game = ClientGame(loop, server_address)
	# Bypass fernando server protection
	@game.on('recv_packet')
	def handle_recv_packet(network, packet_opcode, packet_name, packet_data):
		if packet_opcode == 0xCCF:
			print("Fernando server, bypassing: ", game.network.write_packet("MovementBypass", { "source": { "x": 300, "y": 0 } }))
	# Authenticate on the server
	login_result = await game.authenticate(username, password)
	# Return authentication result
	print("Authentication result: ", login_result)
	if login_result:
		# Apply pincode
		pincode_result = await game.pincode(pincode)
		# Return pincode result
		print("Pincode result: ", pincode_result)
		if pincode_result:
			# Select character
			select_chracter_result = await game.select_char(0)
			# Return select chracter result
			print("Select character result: ", select_chracter_result)
			# While connected
			while game.get_stage() == ClientStage.WORLD:
				# Send chat message
				game.network.write_packet("ChatMessage", { "text": 'Ola servidor'} )
				# Wait 4 seconds
				await asyncio.sleep(0.5)

# Entrypoint
if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	try:
		# start instances of each script
		loop.run_until_complete(asyncio.wait([
			flood_message(loop, "test", "test", pincode = "1111")
		]))
	except KeyboardInterrupt:
		print("Received exit, exiting")
		# get all tasks in progress
		tasks = asyncio.Task.all_tasks(loop)
		# cancel all running tasks
		[ task.cancel() for task in tasks ]
		# process all tasks exceptions
		group = asyncio.gather(*tasks, return_exceptions=True)
		loop.run_until_complete(group)
	finally:
		# close event loop
		loop.close()