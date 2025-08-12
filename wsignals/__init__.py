import asyncio
from asyncio import AbstractEventLoop, Future
from typing import Callable, Coroutine, List, Optional, Union


ListenerType = Callable[..., Optional[bool]]
AsyncCallbackType = Callable[..., Coroutine[None, None, None]]


class AsyncListener:
	callback: AsyncCallbackType
	loop: AbstractEventLoop

	def __init__(self, callback: AsyncCallbackType, loop: Optional[AbstractEventLoop]):
		self.callback = callback
		self.loop = loop or asyncio.get_running_loop()

	def __call__(self, *args, **kwargs):
		loop = self.loop
		if loop.is_closed(): return True
		loop.create_task(self.callback(*args, **kwargs))


class FutureListener:
	future: Future

	def __init__(self, future: Optional[Future] = None, loop: Optional[AbstractEventLoop] = None):
		self.future = future or (loop or asyncio.get_running_loop()).create_future()

	def __call__(self, *args, **kwargs):
		future = self.future
		loop = future.get_loop()
		if future.done() or loop.is_closed(): return True
		loop.call_soon_threadsafe(future.set_result, (args, kwargs))
		return True


class Signal:
	listeners: List[ListenerType]

	def __init__(self):
		self.listeners = list()
	
	def connect_sync(self, listener: ListenerType):
		self.listeners.append(listener)
		return listener
	
	def connect(self, listener: Optional[Union[ListenerType, AsyncCallbackType]] = None, loop: Optional[AbstractEventLoop] = None) -> ListenerType:
		if listener is None:
			return lambda l: self.connect(listener=l, loop=loop)
		
		if asyncio.iscoroutinefunction(listener):
			self.listeners.append(AsyncListener(callback=listener, loop=loop))
		else:
			self.listeners.append(listener)

		return listener
	
	__call__ = connect
	
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
