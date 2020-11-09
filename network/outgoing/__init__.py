# -*- coding: UTF-8 -*-
import os

# Load Extension
extension_python = ".py"

# Load Modules Packets
for file_module in os.listdir(os.path.dirname(__file__)):
    if file_module != '__init__' + extension_python:
        if file_module[-len(extension_python):] == extension_python:
        	module = __import__("network.outgoing." + file_module[:-len(extension_python)], locals(), globals())
