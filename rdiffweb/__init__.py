# Find the version
try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution("rdiffweb").version
except:
    __version__ = "DEV"
