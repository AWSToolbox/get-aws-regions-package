"""
A simple Python package to use as a template.

Attributes:
- __version__: The version of the package, retrieved from the package metadata.
- __all__: A list of all public symbols that the module exports.
"""

import importlib.metadata

from .exceptions import RegionListingError
from .functions import get_region_list

try:
    __version__: str = importlib.metadata.version('wolfsoftware.get_aws_regions')
except importlib.metadata.PackageNotFoundError:
    __version__ = 'unknown'

__all__: list[str] = [
    'RegionListingError',
    'get_region_list'
]
