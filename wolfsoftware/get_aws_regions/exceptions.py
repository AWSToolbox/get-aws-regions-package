"""
This module defines custom exceptions for the wolfsoftware.get-aws-regions package.

Classes:
  - RegionListingError: A custom exception class with a default error message.
"""


class RegionListingError(Exception):
    """
    A custom exception class with a default error message.

    Attributes:
        message (str): The error message for the exception.
    """

    def __init__(self, message: str = "A default error message.") -> None:
        """
        Initialize the RegionListingError with an optional error message.

        Args:
            message (str): The error message for the exception. Defaults to "A default error message.".
        """
        super().__init__(message)
