# Find the version
try:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("rdiffweb").version
except Exception:
    __version__ = "DEV"
