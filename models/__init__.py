# -*- coding: UTF-8 -*-	
from collections import namedtuple

class Object: pass

def dict2obj(data):
	try:
		data = dict(data)
	except (TypeError, ValueError):
		return data
	obj = Object()
	for key, value in data.items():
		obj.__dict__[key] = dict2obj(value)
	return obj