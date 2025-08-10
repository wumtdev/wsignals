import asyncio
from wsignals import Signal


def test_sync():
	my_signal = Signal()
	s1_count = 0
	s2_count = 0

	@my_signal()
	def s1(n, j = None):
		nonlocal s1_count
		s1_count += 1
		assert n == 'n'
		assert j == None
		return True
	
	@my_signal.connect
	def s2(n, j = None):
		nonlocal s2_count
		s2_count += 1
		assert n == 'n'
		assert j == None
	
	assert s1_count == 0
	assert s2_count == 0

	my_signal.call('n')

	assert s1_count == 1
	assert s2_count == 1
	
	my_signal.call('n')
	
	assert s1_count == 1
	assert s2_count == 2

async def t_async():
	my_signal = Signal()

	s1_count = 0
	s2_count = 0
	s3_count = 0

	async def s3():
		nonlocal s3_count
		(n,), _ = await my_signal.next()
		s3_count += 1
		assert n == 'n'
	
	asyncio.create_task(s3())

	await asyncio.sleep(0.01)

	@my_signal()
	def s1(n, j = None):
		nonlocal s1_count
		s1_count += 1
		assert n == 'n'
		assert j == None
		return True
	
	@my_signal
	async def s2(n, j = None):
		nonlocal s2_count
		s2_count += 1
		assert n == 'n'
		assert j == None
	
	assert s1_count == 0
	assert s2_count == 0
	assert s3_count == 0

	my_signal.call('n')

	await asyncio.sleep(0.01)

	assert s1_count == 1
	assert s2_count == 1
	assert s3_count == 1
	
	my_signal.call('n')

	await asyncio.sleep(0.01)
	
	assert s1_count == 1
	assert s2_count == 2
	assert s3_count == 1

def test_1():
	asyncio.run(t_async())
