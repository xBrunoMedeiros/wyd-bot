# -*- coding: UTF-8 -*-
from construct import *
from network.packet import PacketHeader
from network.handler import PacketHandler

# Create position structure
StructPosition = Struct(
	"x"						/ Int16ul,
	"y"						/ Int16ul
)

# Create item structures
StructItemAffect = Struct(
	"index"					/ Int8ul,
	"value"					/ Int8ul
)
StructItem = Struct(
	"index"					/ Int16ul,
	"affects"				/ Array(3, StructItemAffect)
)

# Create position structure
StructScore = Struct(
	"level"					/ Int16ul, # The mob's level
	"defense"				/ Int16ul, # The mob's defense
	"damage"				/ Int16ul, # The mob's damage
	"merchant"				/ Int8ul, # Unknown, The mob's speed	
	"move"					/ BitStruct(
		"direction"	/ BitsInteger(4),
		"speed"		/ BitsInteger(4)
	),
	"max_hp"				/ Int16ul, # The max HP the mob can have
	"max_mp"				/ Int16ul, # The max MP the mob can have
	"cur_hp"				/ Int16ul, # The current HP of the mob
	"cur_mp"				/ Int16ul, # The current MP of the mob

	"str"					/ Int16ul, # The mob's strength points, affects it's attack power
	"int"					/ Int16ul, # The mob's intelligence points, affects it's skill attack powers and MP
	"dex"					/ Int16ul, # The mob's dexterity points, affects it's attack speed
	"con"					/ Int16ul, # The mob's constitution points, affects it's HP

	"special"				/ Array(4, Int8ul) # The mob's special points, affects it's skill tiers
)

# Create packet structures
PacketCreateMob = Struct(
	"header"				/ PacketHeader,
	"position"				/ StructPosition,
	"index"					/ Int16ul,
	"name"					/ FixedSized(16, CString("latin1")), # Weird ( 12 or 16 )
	#"chaos_points"			/ Int8ul,
	#"current_kills"		/ Int8ul,
	#"total_kills"			/ Int16ul,
	"equips"				/ Array(16, Int16ul),
	"affects"				/ Array(16, Int16ul),
	"guild"					/ Int16ul,
	"score"					/ StructScore,
	"create_type"			/ Int16ul, # SpawnType, MemberType
	"anct_code"				/ Array(16, Int8ul),
	"tab"					/ FixedSized(26, CString("latin1")),
	"hold"					/ Int32ul
)

PacketDeleteMob = Struct(
	"header"				/ PacketHeader,
	"delete_type"			/ Enum(Int32ul, Die = 1, Logout = 2)
)

PacketUpdateMob = Struct(
	"header"				/ PacketHeader,
	"max_hp"				/ Int16ul, # The max HP the mob can have
	"max_mp"				/ Int16ul, # The max MP the mob can have
	"cur_hp"				/ Int16ul, # The current HP of the mob
	"cur_mp"				/ Int16ul, # The current MP of the mob
)

PacketMovement = Struct(
	"header"				/ PacketHeader,
	"source"				/ StructPosition,
	"speed"					/ Int32ul,
	"type"					/ Int32ul,
	"command"				/ FixedSized(24, CString("latin1")),
	"destiny"				/ StructPosition
)

# Register packets
PacketHandler.register('CreateMob', PacketCreateMob, 0x364, recv = True)
PacketHandler.register('DeleteMob', PacketDeleteMob, 0x165, recv = True)
PacketHandler.register('UpdateMob', PacketUpdateMob, 0x181, recv = True)
PacketHandler.register('Movement', PacketMovement, 0x36C, recv = True)