import asyncio
from asyncio import AbstractEventLoop, Future
from dataclasses import dataclass
from typing import Callable, Coroutine, List, Optional


type IListener = Callable[..., None | bool]
type IAsyncCallback = Callable[..., Coroutine[None, None, None]]

@dataclass
class AsyncListener:
	callback: IAsyncCallback
	loop: AbstractEventLoop

	def __call__(self, *args, **kwargs):
		loop = self.loop
		if loop.is_closed(): return True
		loop.create_task(self.callback(*args, **kwargs))

@dataclass
class FutureListener:
	future: Future

	def __call__(self, *args, **kwargs):
		future = self.future
		loop = future.get_loop()
		if future.done() or loop.is_closed(): return True
		loop.call_soon_threadsafe(future.set_result, (args, kwargs))
		return True

class Signal:
	listeners: List[IListener]

	def __init__(self):
		self.listeners = list()
	
	def connect(self, listener: IListener):
		self.listeners.append(listener)
	
	def __call__(self, listener: IListener) -> IListener:
		self.listeners.append(listener)
		return listener
	
	def connect_async(self, callback: IAsyncCallback, loop: Optional[AbstractEventLoop] = None):
		if not loop:
			loop = asyncio.get_running_loop()
		self.listeners.append(AsyncListener(callback=callback, loop=loop))
	
	def next(self, future: Optional[Future] = None, loop: Optional[AbstractEventLoop] = None) -> Future:
		if not future:
			if not loop: loop = asyncio.get_running_loop()
			future = loop.create_future()
		self.listeners.append(FutureListener(future=future))
		return future

	def call(self, *args, **kwargs):
		listeners = self.listeners
		i = len(listeners)
		for listener in listeners[::-1]:
			i -= 1
			if listener(*args, **kwargs):
				del listeners[i]
