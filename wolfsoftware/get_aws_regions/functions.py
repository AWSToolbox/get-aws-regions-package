"""
This module provides functionalities for retrieving and processing AWS region information with support for multiple AWS profiles.

Capabilities:
  - Fetching a list of all AWS regions, with the option to include or exclude regions based on account opt-in status.
  - Retrieving the geographical location description for a specific AWS region from the AWS Systems Manager (SSM) Parameter Store.
  - Fetching geographical locations for multiple AWS regions using concurrent threading for improved performance.
  - Applying include and exclude filters to the list of regions to customize the output.
  - Generating a comprehensive list of AWS regions, with optional detailed information about each region.
  - Utilizing different AWS profiles for the retrieval of region information.

Functions:
  - get_region_list: Main function to retrieve a list of AWS regions, optionally filtering by include and exclude lists,
    and returning detailed information if required.

Private Functions:
  - _fetch_all_regions: Retrieves a list of all AWS regions.
  - _fetch_region_description: Fetches the geographical location for a specific AWS region.
  - _fetch_region_descriptions: Fetches geographical locations for multiple AWS regions using threading.
  - _apply_region_filters: Applies include and exclude filters to the list of regions.

Exceptions:
  - RegionListingError: Custom exception class to handle errors related to AWS region retrieval and processing.

Dependencies:
  - boto3: AWS SDK for Python to interact with various AWS services like EC2 and SSM.
  - concurrent.futures: Standard library module to enable asynchronous execution using threading.
  - botocore.exceptions: Exceptions for handling errors during boto3 operations.

Usage:
  This module is intended to be used as part of the wolfsoftware.get-aws-regions package.
  The main entry point is the `get_region_list` function, which provides flexibility in retrieving
  and customizing the list of AWS regions based on user-defined criteria, including the ability
  to specify different AWS profiles.
"""

from typing import Any, List, Dict, Optional, Union

from concurrent.futures._base import Future
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3  # pylint: disable=import-error
from botocore.exceptions import BotoCoreError, ClientError

from .exceptions import RegionListingError


def _fetch_all_regions(all_regions: bool = True, profile_name: Optional[str] = None) -> List[Dict[str, Union[str, bool]]]:
    """
    Retrieve a list of all AWS regions.

    Arguments:
        all_regions (bool): If True, list all available regions, including those not opted into.
                            If False, list only regions opted into by the account.
        profile_name (Optional[str]): The name of the AWS profile to use.

    Returns:
        List[Dict[str, Union[str, bool]]]: A list of dictionaries containing information about each region.

    Raises:
        RegionListingError: If there is an error in retrieving the regions.
    """
    try:
        # Initialize a session using Amazon EC2 with the specified profile
        session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        ec2: Any = session.client('ec2')

        # Retrieve a list of all available regions or only opted-in regions based on the flag
        if all_regions:
            response: Any = ec2.describe_regions(AllRegions=True)
        else:
            response: Any = ec2.describe_regions()

        # We only keep RegionName and OptInStatus
        regions: List[Dict[str, Any]] = [
            {"RegionName": region['RegionName'], "OptInStatus": region['OptInStatus']}
            for region in response['Regions']
        ]

        return regions

    except (BotoCoreError, ClientError) as e:
        raise RegionListingError(f"An error occurred while listing regions: {str(e)}") from e
    except Exception as e:
        raise RegionListingError(f"An unexpected error occurred: {str(e)}") from e


def _fetch_region_description(region_name: str, profile_name: Optional[str] = None) -> Dict[str, str]:
    """
    Fetch the geographical location for a specific AWS region from SSM Parameter Store.

    Arguments:
        region_name (str): The name of the region to fetch the geographical location for.
        profile_name (Optional[str]): The name of the AWS profile to use.

    Returns:
        Dict[str, str]: A dictionary containing the region name and its geographical location.

    Raises:
        RegionListingError: If there is an error in retrieving the region geographical location.
    """
    try:
        # Initialize a session using Amazon SSM with the specified profile
        session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        ssm: Any = session.client('ssm')

        # Retrieve the parameter for the region description
        parameter_name: str = f"/aws/service/global-infrastructure/regions/{region_name}/longName"
        response: Any = ssm.get_parameter(Name=parameter_name)

        return {region_name: response['Parameter']['Value']}

    except (BotoCoreError, ClientError) as e:
        raise RegionListingError(f"An error occurred while retrieving geographical location for region {region_name}: {str(e)}") from e
    except Exception as e:
        raise RegionListingError(f"An unexpected error occurred: {str(e)}") from e


def _fetch_region_descriptions(region_names: List[str], profile_name: Optional[str] = None) -> Dict[str, str]:
    """
    Fetch geographical locations for multiple AWS regions from SSM Parameter Store using threading for better performance.

    Arguments:
        region_names (List[str]): A list of region names to fetch geographical locations for.
        profile_name (Optional[str]): The name of the AWS profile to use.

    Returns:
        Dict[str, str]: A dictionary mapping region codes to their geographical locations.

    Raises:
        RegionListingError: If there is an error in retrieving the region geographical locations.
    """
    descriptions: Dict = {}

    with ThreadPoolExecutor() as executor:
        future_to_region: Dict[Future[Dict[str, str]], str] = {
            executor.submit(_fetch_region_description, region, profile_name): region
            for region in region_names
        }

        for future in as_completed(future_to_region):
            region: str = future_to_region[future]
            try:
                result: Dict[str, str] = future.result()
                descriptions.update(result)
            except Exception as e:
                raise RegionListingError(f"An unexpected error occurred while fetching geographical locations for {region}: {str(e)}") from e

    return descriptions


def _apply_region_filters(
    regions: List[Dict[str, Union[str, bool]]],
    include_list: Optional[List[str]] = None,
    exclude_list: Optional[List[str]] = None
) -> List[Dict[str, Union[str, bool]]]:
    """
    Apply include and exclude filters to the list of regions.

    Arguments:
        regions (List[Dict[str, Union[str, bool]]]): The list of regions to filter.
        include_list (Optional[List[str]]): A list of regions to include. Only these regions will be returned if specified.
        exclude_list (Optional[List[str]]): A list of regions to exclude. These regions will be omitted from the returned list if specified.

    Returns:
        List[Dict[str, Union[str, bool]]]: A sorted list of regions after applying the filters.
    """
    if include_list is not None:
        regions = [region for region in regions if region['RegionName'] in include_list]

    if exclude_list is not None:
        regions = [region for region in regions if region['RegionName'] not in exclude_list]

    # Sort regions alphabetically by Region
    regions.sort(key=lambda x: x['RegionName'])

    return regions


def get_region_list(
    include_list: Optional[List[str]] = None,
    exclude_list: Optional[List[str]] = None,
    all_regions: Optional[bool] = True,
    details: Optional[bool] = False,
    profile_name: Optional[str] = None
) -> Union[List[Dict[str, Union[str, bool]]], List[str]]:
    """
    Retrieve a list of AWS regions, optionally filtering by include and exclude lists.

    Optionally return detailed information about each region or just the region names.

    Arguments:
        include_list (Optional[List[str]]): A list of regions to include. Only these regions will be returned if specified.
        exclude_list (Optional[List[str]]): A list of regions to exclude. These regions will be omitted from the returned list if specified.
        all_regions (bool): If True, list all available regions, including those not opted into. If False, list only regions opted into by the account.
        details (bool): If True, return detailed information about each region. If False, return only the region names.
        profile_name (Optional[str]): The name of the AWS profile to use.

    Returns:
        Union[List[Dict[str, Union[str, bool]]], List[str]]: A sorted list of regions with detailed information or just the region names.

    Raises:
        RegionListingError: If there is an error in retrieving the regions.
    """
    try:
        all_regions_list: List[Dict[str, str | bool]] = _fetch_all_regions(all_regions, profile_name)
    except Exception as e:
        raise RegionListingError(f"An error occurred while retrieving regions: {str(e)}") from e

    filtered_regions: List[Dict[str, str | bool]] = _apply_region_filters(all_regions_list, include_list, exclude_list)

    if details:
        region_names: List[str | bool] = [region['RegionName'] for region in filtered_regions]
        region_descriptions: Dict[str, str] = _fetch_region_descriptions(region_names, profile_name)
        for region in filtered_regions:
            region['GeographicalLocation'] = region_descriptions.get(region['RegionName'], "Unknown")
        print("Filtered Regions with Details:", filtered_regions)  # Debug print
        return filtered_regions
    return [region['RegionName'] for region in filtered_regions]
