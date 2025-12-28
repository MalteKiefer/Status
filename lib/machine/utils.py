import os
import re
from glob import glob


def _validate_custom_root_path(path: str) -> str:
	"""Validate and normalize custom root path from environment."""
	if not path:
		return ""
	# Normalize path to remove redundant separators and resolve . and ..
	normalized = os.path.normpath(path)
	# Must be absolute path to prevent relative path traversal
	if not os.path.isabs(normalized):
		return ""
	# Ensure path exists and is a directory
	if not os.path.isdir(normalized):
		return ""
	return normalized


try:
	CUSTOM_ROOT_PATH = _validate_custom_root_path(os.environ["STATUS_CUSTOM_ROOT_PATH"])
except KeyError:
	CUSTOM_ROOT_PATH = ""


def get(path: str, isint: bool = False, fallback = None):
	try:
		if CUSTOM_ROOT_PATH:
			custom_path = CUSTOM_ROOT_PATH + path
			if os.path.exists(custom_path):
				path = custom_path
		with open(path, "r") as f:
			val = f.read().rstrip()
		res = int(val) if isint else val
	except (FileNotFoundError, ValueError):
		res = fallback
	return res


def grep(contents: str, keyword: str):
	for line in contents.split("\n"):
		if keyword in line:
			return re.sub(r'[^0-9]', '', line)


def temp_val(raw_value: int):
	if (len(str(raw_value))) >= 4:
		raw_value /= 1000

	return raw_value


def ls(path: str):
	try:
		if CUSTOM_ROOT_PATH:
			custom_path = CUSTOM_ROOT_PATH + path
			if os.path.exists(custom_path):
				path = custom_path
		files = [os.path.join(path, f) for f in os.listdir(path)]
		return sorted(files)
	except (FileNotFoundError, NotADirectoryError, PermissionError):
		return []


def ls_glob(path: str, target: str):
	if CUSTOM_ROOT_PATH:
		custom_path = CUSTOM_ROOT_PATH + path
		if os.path.exists(custom_path):
			path = custom_path
	files = glob(os.path.join(path, target))
	return sorted(files)


def basename(path: str):
	return path.split("/")[-1]


def parse_temperature(temp: int, divide: bool = True):
	if not temp: return temp
	return temp / 1000 if divide else temp