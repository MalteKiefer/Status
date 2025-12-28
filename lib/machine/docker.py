import subprocess
import json

from lib.config import config


class Docker:

	@staticmethod
	def is_available():
		"""Check if Docker is installed and accessible."""
		try:
			result = subprocess.run(
				["docker", "info"],
				capture_output=True,
				timeout=5
			)
			return result.returncode == 0
		except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
			return False

	@staticmethod
	def get_containers():
		"""Get list of all containers with their details."""
		try:
			result = subprocess.run(
				["docker", "ps", "-a", "--format", "{{json .}}"],
				capture_output=True,
				text=True,
				timeout=10
			)
			if result.returncode != 0:
				return []

			containers = []
			for line in result.stdout.strip().split("\n"):
				if not line:
					continue
				try:
					container = json.loads(line)
					containers.append({
						"id": container.get("ID", ""),
						"name": container.get("Names", ""),
						"image": container.get("Image", ""),
						"status": container.get("Status", ""),
						"state": container.get("State", ""),
						"ports": container.get("Ports", ""),
						"created": container.get("CreatedAt", "")
					})
				except json.JSONDecodeError:
					continue
			return containers
		except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
			return []

	@staticmethod
	def get_stats():
		"""Get resource usage statistics for running containers."""
		try:
			result = subprocess.run(
				["docker", "stats", "--no-stream", "--format", "{{json .}}"],
				capture_output=True,
				text=True,
				timeout=15
			)
			if result.returncode != 0:
				return []

			stats = []
			for line in result.stdout.strip().split("\n"):
				if not line:
					continue
				try:
					stat = json.loads(line)
					stats.append({
						"id": stat.get("ID", ""),
						"name": stat.get("Name", ""),
						"cpu": stat.get("CPUPerc", "0%"),
						"memory": stat.get("MemUsage", ""),
						"memory_percent": stat.get("MemPerc", "0%"),
						"net_io": stat.get("NetIO", ""),
						"block_io": stat.get("BlockIO", "")
					})
				except json.JSONDecodeError:
					continue
			return stats
		except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
			return []

	def get_info(self):
		"""Get Docker information summary."""
		if not config.get("docker", "enabled"):
			return None
		if not self.is_available():
			return None

		containers = self.get_containers()
		stats = self.get_stats()

		# Create stats lookup by container name
		stats_by_name = {s["name"]: s for s in stats}

		# Merge stats into container info
		for container in containers:
			name = container["name"]
			if name in stats_by_name:
				container["cpu"] = stats_by_name[name]["cpu"]
				container["memory"] = stats_by_name[name]["memory"]
				container["memory_percent"] = stats_by_name[name]["memory_percent"]
				container["net_io"] = stats_by_name[name]["net_io"]
				container["block_io"] = stats_by_name[name]["block_io"]

		running = sum(1 for c in containers if c["state"] == "running")
		stopped = len(containers) - running

		return {
			"available": True,
			"running": running,
			"stopped": stopped,
			"total": len(containers),
			"containers": containers
		}
