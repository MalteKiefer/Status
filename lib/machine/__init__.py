from .cpu import CPU
from .memory import Memory
from .storage import Storage
from .network import Network
from .host import Host
from .docker import Docker


class Machine:

	def __init__(self):
		self.cpu = CPU()
		self.memory = Memory()
		self.storage = Storage()
		self.network = Network()
		self.host = Host()
		self.docker = Docker()

	async def get_full_info(self):
		return {
			"cpu": (await self.cpu.get_full_info()),
			"memory": self.memory.get_usage(),
			"storage": self.storage.get_usage(),
			"network": self.network.get_net(),
			"host": self.host.get_host(),
			"docker": self.docker.get_info()
		}
