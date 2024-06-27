"""
Configuration for pytest tests, including fixtures and mock data for testing the wolfsoftware.get-aws-regions package.

Fixtures:
- boto3_session_mock: Mocks the boto3 session for AWS interactions.
- boto3_session_mock_with_exception: Mocks the boto3 session raising an exception during describe_regions.

Mock Data:
- mock_regions: A list of dictionaries representing mock AWS regions.
- mock_description: A dictionary representing the mock description of a specific AWS region.
"""

from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, patch
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
def boto3_session_mock() -> Generator[MagicMock, None, None]:
    """
    Fixture to mock the boto3 session.

    Yields:
        MagicMock: A mock of the boto3 session.
    """
    with patch("boto3.Session") as mock_session:
        mock_session_instance: Any = mock_session.return_value

        regions_mock = MagicMock()
        ssm_mock = MagicMock()

        def mock_get_parameter(Name) -> Dict[str, Dict[str, str]]:
            if Name in mock_description:
                return {"Parameter": {"Value": mock_description[Name]}}
            raise ValueError(f"Unknown parameter name: {Name}")

        ssm_mock.get_parameter.side_effect = mock_get_parameter

        mock_session_instance.client.side_effect = lambda service_name, *args, **kwargs: ssm_mock if service_name == "ssm" else regions_mock

        regions_mock.describe_regions.return_value = {"Regions": mock_regions}

        yield mock_session


@pytest.fixture
def boto3_session_mock_with_exception() -> Generator[MagicMock, None, None]:
    """
    Fixture to mock the boto3 session raising an exception during describe_regions.

    Yields:
        MagicMock: A mock of the boto3 session.
    """
    with patch("boto3.Session") as mock_session:
        mock_session_instance: Any = mock_session.return_value

        regions_mock = MagicMock()
        ssm_mock = MagicMock()

        def mock_get_parameter(Name) -> Dict[str, Dict[str, str]]:
            if Name in mock_description:
                return {"Parameter": {"Value": mock_description[Name]}}
            raise ValueError(f"Unknown parameter name: {Name}")

        ssm_mock.get_parameter.side_effect = mock_get_parameter

        regions_mock.describe_regions.side_effect = Exception("Test Exception")

        mock_session_instance.client.side_effect = lambda service_name, *args, **kwargs: ssm_mock if service_name == "ssm" else regions_mock

        yield mock_session
