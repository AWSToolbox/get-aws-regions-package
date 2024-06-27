"""
Configuration for pytest tests, including fixtures and mock data for testing the wolfsoftware.get-aws-regions package.

Fixtures:
- boto3_client_mock: Mocks the boto3 client for AWS interactions.

Mock Data:
- mock_regions: A list of dictionaries representing mock AWS regions.
- mock_description: A dictionary representing the mock description of a specific AWS region.
"""
from typing import Any, Dict, Generator, List, Union

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Mock data
mock_regions: List[Dict[str, str]] = [
    {"RegionName": "us-east-1", "OptInStatus": "opt-in-not-required"},
    {"RegionName": "us-west-1", "OptInStatus": "opt-in-not-required"},
    {"RegionName": "eu-west-1", "OptInStatus": "opted-in"}
]

mock_description: Dict[str, str] = {
    "/aws/service/global-infrastructure/regions/us-east-1/longName": "US East (N. Virginia)",
    "/aws/service/global-infrastructure/regions/us-west-1/longName": "US West (N. California)",
    "/aws/service/global-infrastructure/regions/eu-west-1/longName": "EU West (Ireland)"
}


@pytest.fixture
def boto3_client_mock(mock_exception: Union[Exception, None] = None) -> Generator[Union[MagicMock, AsyncMock], Any, None]:
    """
    Fixture to mock the boto3 client.

    Yields:
        MagicMock: A mock of the boto3 client.
    """
    with patch("boto3.client") as mock_client:
        regions_mock = MagicMock()
        ssm_mock = MagicMock()

        def mock_get_parameter(Name) -> Dict[str, Dict[str, str]]:
            if Name in mock_description:
                return {"Parameter": {"Value": mock_description[Name]}}
            raise ValueError(f"Unknown parameter name: {Name}")

        ssm_mock.get_parameter.side_effect = mock_get_parameter
        mock_client.side_effect = lambda service_name, *args, **kwargs: ssm_mock if service_name == "ssm" else regions_mock

        # Conditionally set side effect for describe_regions based on mock_exception
        if mock_exception:
            print("HERE")
            regions_mock.describe_regions.side_effect = mock_exception
        regions_mock.describe_regions.side_effect = mock_exception
        regions_mock.describe_regions.return_value = {"Regions": mock_regions}

        yield mock_client


@pytest.fixture
def boto3_client_mock_with_exception() -> Generator[MagicMock, None, None]:
    """
    Fixture to mock the boto3 client raising an exception during describe_regions.

    Yields:
        MagicMock: A mock of the boto3 client.
    """
    with patch("boto3.client") as mock_client:
        regions_mock = MagicMock()
        ssm_mock = MagicMock()

        def mock_get_parameter(Name) -> Dict[str, Dict[str, str]]:
            if Name in mock_description:
                return {"Parameter": {"Value": mock_description[Name]}}
            raise ValueError(f"Unknown parameter name: {Name}")

        ssm_mock.get_parameter.side_effect = mock_get_parameter

        regions_mock.describe_regions.side_effect = Exception("Test Exception")

        mock_client.side_effect = lambda service_name, *args, **kwargs: ssm_mock if service_name == "ssm" else regions_mock

        yield mock_client
