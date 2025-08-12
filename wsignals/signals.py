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
	'''
	Entity representing a single event type.

	Signal stores listeners and executes them when it get called (event occurs).
	'''

	listeners: List[ListenerType]

	def __init__(self):
		'''Initializes new empty signal'''
		self.listeners = list()
	
	def connect_sync(self, listener: ListenerType):
		'''Registers a sync listener to the signal.
		Args:
			listener: The sync listener to register.
		Returns:
			The registered listener.
		'''
		self.listeners.append(listener)
		return listener
	
	def connect_async(self, listener: AsyncCallbackType, loop: Optional[AbstractEventLoop] = None):
		'''Registers an async listener to the signal.
		Args:
			listener: The async listener to register.
			loop: The event loop to use for the listener. Defaults to current running loop.
		Returns:
			The registered listener.
		'''
		self.listeners.append(AsyncListener(callback=listener, loop=loop))
		return listener
	
	def connect(self, listener: Optional[Union[ListenerType, AsyncCallbackType]] = None, loop: Optional[AbstractEventLoop] = None) -> ListenerType:
		'''
		Registers a listener (synchronous or asynchronous) to the signal.

		Can be used as a decorator (`@signal.connect`) or as a method (`signal.connect(listener)`).

		Args:
			listener: The listener function to register. Can be synchronous or asynchronous.
			loop: The event loop for asynchronous listeners. Defaults to the current running loop.
		Returns:
			The registered listener or a decorator.
		'''
		if listener is None:
			return lambda l: self.connect(listener=l, loop=loop)
		
		if asyncio.iscoroutinefunction(listener):
			self.connect_async(listener, loop=loop)
		else:
			self.connect_sync(listener)

		return listener
	
	__call__ = connect
	
	def next(self, future: Optional[Future] = None, loop: Optional[AbstractEventLoop] = None) -> Future:
		'''
		Wait for the next signal call.

		Use it to wait for a single signal call in async code.

		Args:
			future: An existing Future to resolve, instead of creating a new one.
			loop: The event loop to use for the Future. Defaults to the current running loop.
		Returns:
			A Future waiting for the next signal call, resolving call (args, kwargs).
		'''
		if not future:
			if not loop: loop = asyncio.get_running_loop()
			future = loop.create_future()
		self.listeners.append(FutureListener(future=future))
		return future

	def call(self, *args, **kwargs):
		'''
		Calls each listener with the provided arguments.

		Each listener is called with *args and **kwargs. If a listener returns True,
		it is removed from the listeners list.
		Args:
			*args: Positional arguments to pass to each listener.
			**kwargs: Keyword arguments to pass to each listener.
		'''

		listeners = self.listeners
		i = len(listeners)
		for listener in listeners[::-1]:
			i -= 1
			if listener(*args, **kwargs):
				del listeners[i]
