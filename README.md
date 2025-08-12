
# wsignals
v0.2.3

Library for event emitting and handling


## Installation

### PyPI
```sh
pip install wsignals
```

### GitHub
```sh
pip install git+https://github.com/wumtdev/wsignals.git
```

### Manual
Clone from github
```sh
# using https
git clone https://github.com/wumtdev/wsignals.git
# using ssh
git clone git@github.com:wumtdev/wsignals.git
```

In the environment where you need to install library, install it as a local package. Specify path to cloned repository.
```sh
pip install /path/to/cloned_repo
```


## Usage

### Simple
```py
from wsignals import Signal

on_start = Signal()

@on_start
def log_start():
	print('started')

on_start.call()
```

### Class + Async
```py
import asyncio
from wsignals import Signal

class Dog:
	def __init__(self, name: str):
		self.on_bark = Signal()
		self.name = name
	
	def bark(self, msg: str):
		print('bark!')
		self.on_bark.call(msg)

async def main():
	gamma = Dog('Gamma')
	
	@gamma.on_bark
	async def handle_gamma_bark(msg):
		print(f'Gamma barked: {msg}')
	
	gamma.bark()

asyncio.run(main())
```
