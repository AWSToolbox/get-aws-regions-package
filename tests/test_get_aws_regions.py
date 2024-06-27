"""
Pytest tests for the wolfsoftware.get-aws-regions package, focusing on the public function get_region_list.

Tests:
- test_get_region_list_all_regions: Tests fetching all regions with detailed information.
- test_get_region_list_include_filter: Tests fetching regions with an include filter.
- test_get_region_list_exclude_filter: Tests fetching regions with an exclude filter.
- test_get_region_list_no_details: Tests fetching region names without details.
- test_get_region_list_exceptions: Tests exception handling when an error occurs in fetching regions.
"""

from typing import Any, Dict, List, Optional

import importlib.metadata
import pytest

from wolfsoftware.get_aws_regions import get_region_list, RegionListingError

from .conftest import mock_regions


def test_version() -> None:
    """
    Test to ensure the version of the Package is set and not 'unknown'.

    This test retrieves the version of the package using importlib.metadata and asserts that the version
    is not None and not 'unknown'.
    """
    version: Optional[str] = None

    try:
        version = importlib.metadata.version('wolfsoftware.get_aws_regions')
    except importlib.metadata.PackageNotFoundError:
        version = None

    assert version is not None, "Version should be set"  # nosec: B101
    assert version != 'unknown', f"Expected version, but got {version}"  # nosec: B101


def test_get_region_list_all_regions(boto3_session_mock) -> None:
    """
    Test fetching all regions with detailed information.

    Arguments:
        boto3_session_mock (fixture): The mocked boto3 session.
    """
    regions_mock: Any = boto3_session_mock.return_value.client.return_value
    regions_mock.describe_regions.return_value = {"Regions": mock_regions}

    result: List[Dict[str, str | bool]] | List[str] = get_region_list(details=True)
    result.sort(key=lambda x: x["RegionName"])  # Sort the result for consistent ordering

    expected_result: List[Dict[str, str]] = [
        {"RegionName": "us-east-1", "OptInStatus": "opt-in-not-required", "GeographicalLocation": "US East (N. Virginia)"},
        {"RegionName": "us-west-1", "OptInStatus": "opt-in-not-required", "GeographicalLocation": "US West (N. California)"},
        {"RegionName": "eu-west-1", "OptInStatus": "opted-in", "GeographicalLocation": "EU West (Ireland)"}
    ]
    expected_result.sort(key=lambda x: x["RegionName"])  # Sort the expected result for consistent ordering

    assert result == expected_result  # nosec: B101


def test_get_region_list_include_filter(boto3_session_mock) -> None:
    """
    Test fetching regions with an include filter.

    Arguments:
        boto3_session_mock (fixture): The mocked boto3 session.
    """
    regions_mock: Any = boto3_session_mock.return_value.client.return_value

    regions_mock.describe_regions.return_value = {"Regions": mock_regions}

    result: List[Dict[str, str | bool]] | List[str] = get_region_list(include_list=["us-east-1", "eu-west-1"], details=True)
    result.sort(key=lambda x: x["RegionName"])  # Sort the result for consistent ordering

    expected_result: List[Dict[str, str]] = [
        {"RegionName": "us-east-1", "OptInStatus": "opt-in-not-required", "GeographicalLocation": "US East (N. Virginia)"},
        {"RegionName": "eu-west-1", "OptInStatus": "opted-in", "GeographicalLocation": "EU West (Ireland)"}
    ]
    expected_result.sort(key=lambda x: x["RegionName"])  # Sort the expected result for consistent ordering

    assert result == expected_result  # nosec: B101


def test_get_region_list_exclude_filter(boto3_session_mock) -> None:
    """
    Test fetching regions with an exclude filter.

    Arguments:
        boto3_session_mock (fixture): The mocked boto3 session.
    """
    regions_mock: Any = boto3_session_mock.return_value.client.return_value

    regions_mock.describe_regions.return_value = {"Regions": mock_regions}

    result: List[Dict[str, str | bool]] | List[str] = get_region_list(exclude_list=["us-west-1"], details=True)
    result.sort(key=lambda x: x["RegionName"])  # Sort the result for consistent ordering

    expected_result: List[Dict[str, str]] = [
        {"RegionName": "us-east-1", "OptInStatus": "opt-in-not-required", "GeographicalLocation": "US East (N. Virginia)"},
        {"RegionName": "eu-west-1", "OptInStatus": "opted-in", "GeographicalLocation": "EU West (Ireland)"}
    ]
    expected_result.sort(key=lambda x: x["RegionName"])  # Sort the expected result for consistent ordering

    assert result == expected_result  # nosec: B101


def test_get_region_list_no_details(boto3_session_mock) -> None:
    """
    Test fetching region names without details.

    Arguments:
        boto3_session_mock (fixture): The mocked boto3 session.
    """
    regions_mock: Any = boto3_session_mock.return_value.client.return_value

    regions_mock.describe_regions.return_value = {"Regions": mock_regions}

    result: List[Dict[str, str | bool]] | List[str] = get_region_list(details=False)
    result.sort()  # Sort the result for consistent ordering

    expected_result: List[str] = ["us-east-1", "us-west-1", "eu-west-1"]
    expected_result.sort()  # Sort the expected result for consistent ordering

    assert result == expected_result  # nosec: B101


def test_get_region_list_exceptions(boto3_session_mock_with_exception) -> None:  # pylint: disable=unused-argument
    """
    Test exception handling when an error occurs in fetching regions.

    Arguments:
        boto3_session_mock (fixture): The mocked boto3 session.
    """
    # Use pytest.raises to catch RegionListingError
    with pytest.raises(RegionListingError) as excinfo:
        get_region_list()

    # Verify the exception message
    assert str(excinfo.value).endswith("Test Exception")  # nosec: B101
