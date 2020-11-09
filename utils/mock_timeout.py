# -*- coding: UTF-8 -*-
import time
import asyncio
from mock import Mock

class MockTimeout(Mock):
	
	async def wait(self, timeout = None):
		start = time.time()
		while (timeout is None or time.time() - start <= timeout) and not self.called:
			await asyncio.sleep(0.05)
		return self.called