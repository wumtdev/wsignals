import asyncio
from asyncio import CancelledError
import time

from wsignals import Signal


DELAY = 3.0
on_tick = Signal()
stop = False

def sync_timer():
	while not stop:
		print('sync_timer: sleeping')
		time.sleep(DELAY)
		print('sync_timer: calling')
		on_tick.call()
		print('sync_timer: called')

async def timer():
	while True:
		print('timer: sleeping')
		await asyncio.sleep(DELAY)
		print('timer: calling')
		on_tick.call()
		print('timer: called')

def sync_handler():
	print('sync_handler: tick handled')

async def main():
	loop = asyncio.get_running_loop()
	print('main: starting timer')
	# asyncio.create_task(timer())
	loop.run_in_executor(None, sync_timer)
	print('main: timer started')

	on_tick.connect(sync_handler)

	@on_tick
	async def async_handler():
		print('async_handler: tick handled')

	try:
		while True:
			print('main: waiting tick')
			await on_tick.next()
			print('main: tick handled')
	except CancelledError:
		global stop
		stop = True

if __name__ == '__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print('keyboard interrupted')
