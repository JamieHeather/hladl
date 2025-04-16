from importlib.metadata import version, PackageNotFoundError

# Whole-package versioning
try:
    __version__ = version('hladl')
except PackageNotFoundError:
    __version__ = "unknown"
