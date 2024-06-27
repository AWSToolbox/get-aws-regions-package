<!-- markdownlint-disable -->
<p align="center">
    <a href="https://github.com/AWSToolbox/">
        <img src="https://cdn.wolfsoftware.com/assets/images/github/organisations/awstoolbox/black-and-white-circle-256.png" alt="AWSToolbox logo" />
    </a>
    <br />
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/actions/workflows/cicd.yml">
        <img src="https://img.shields.io/github/actions/workflow/status/AWSToolbox/get-aws-regions-package/cicd.yml?branch=master&label=build%20status&style=for-the-badge" alt="Github Build Status" />
    </a>
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/blob/master/LICENSE.md">
        <img src="https://img.shields.io/github/license/AWSToolbox/get-aws-regions-package?color=blue&label=License&style=for-the-badge" alt="License">
    </a>
    <a href="https://github.com/AWSToolbox/get-aws-regions-package">
        <img src="https://img.shields.io/github/created-at/AWSToolbox/get-aws-regions-package?color=blue&label=Created&style=for-the-badge" alt="Created">
    </a>
    <br />
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/releases/latest">
        <img src="https://img.shields.io/github/v/release/AWSToolbox/get-aws-regions-package?color=blue&label=Latest%20Release&style=for-the-badge" alt="Release">
    </a>
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/releases/latest">
        <img src="https://img.shields.io/github/release-date/AWSToolbox/get-aws-regions-package?color=blue&label=Released&style=for-the-badge" alt="Released">
    </a>
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/releases/latest">
        <img src="https://img.shields.io/github/commits-since/AWSToolbox/get-aws-regions-package/latest.svg?color=blue&style=for-the-badge" alt="Commits since release">
    </a>
    <br />
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/blob/master/.github/CODE_OF_CONDUCT.md">
        <img src="https://img.shields.io/badge/Code%20of%20Conduct-blue?style=for-the-badge" />
    </a>
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/blob/master/.github/CONTRIBUTING.md">
        <img src="https://img.shields.io/badge/Contributing-blue?style=for-the-badge" />
    </a>
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/blob/master/.github/SECURITY.md">
        <img src="https://img.shields.io/badge/Report%20Security%20Concern-blue?style=for-the-badge" />
    </a>
    <a href="https://github.com/AWSToolbox/get-aws-regions-package/issues">
        <img src="https://img.shields.io/badge/Get%20Support-blue?style=for-the-badge" />
    </a>
</p>

## Overview

This module provides a simple method for retrieving and processing AWS region information. This is a core component
for all of the tools in our [AWS Toolbox](https://github.com/AWSToolbox).

### Features

- **Fetching AWS Regions**:
  - Retrieve a list of all AWS regions, optionally including/excluding regions based on account opt-in status.
  - Supports fetching detailed information about each region.

- **Region Details**:
  - Fetch geographical location descriptions for specific AWS regions from the AWS Systems Manager (SSM) Parameter Store.
  - Utilizes concurrent threading for enhanced performance when fetching multiple region details.

- **Filtering**:
  - Apply include and exclude filters to customize the list of AWS regions returned.

### Functions

#### Public Functions

- **get_region_list**
  - Retrieves a list of AWS regions.
  - Parameters:
    - `include_list`: Optional list of regions to include.
    - `exclude_list`: Optional list of regions to exclude.
    - `all_regions`: Boolean flag to include all regions (default: True).
    - `details`: Boolean flag to return detailed information about each region (default: False).
  - Returns:
    - If `details=True`: Sorted list of dictionaries containing detailed region information.
    - If `details=False`: Sorted list of region names as strings.
  - Raises:
    - `RegionListingError`: If an error occurs during region retrieval or processing.

### Usage

This module is designed to be used as part of the `wolfsoftware.get-aws-regions` package. The primary function, `get_region_list`, allows flexible retrieval and customization of AWS region information based on user-defined criteria.

### Example

```python
from wolfsoftware.get_aws_regions import get_region_list

# Example usage: Retrieve all regions and print their names
regions = get_region_list(details=False)
print("AWS Regions:", regions)

# Example usage: Retrieve detailed information for selected regions
detailed_regions = get_region_list(include_list=['us-west-1', 'us-east-1'], details=True)
for region in detailed_regions:
    print(f"Region: {region['RegionName']}, Location: {region['GeographicalLocation']}")
```

### Notes

- Ensure AWS credentials are properly configured for API access.
- Error handling is integrated to manage exceptions during AWS operations.
- Threading is utilized for efficient concurrent operations when fetching region details.

For further details and customization options, refer to the function docstrings and the module's implementation.

<br />
<p align="right"><a href="https://wolfsoftware.com/"><img src="https://img.shields.io/badge/Created%20by%20Wolf%20on%20behalf%20of%20Wolf%20Software-blue?style=for-the-badge" /></a></p>
