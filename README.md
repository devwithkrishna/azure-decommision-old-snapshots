# Azure Decommission Old Snapshots

This repository automates the cleanup of outdated Azure snapshots by identifying and listing snapshots older than a specified number of days. It uses Azure Resource Graph queries to fetch snapshot details and logs the results for further processing.

## Features

- Identify Azure snapshots older than a specified number of days.
- Fetch subscription IDs dynamically using subscription names.
- Paginated querying for large datasets to handle thousands of snapshots efficiently.
- Logging support for debugging and monitoring.

## Prerequisites

1. **Python**: Ensure Python 3.8+ is installed.
2. **Azure CLI**: Install and authenticate using the Azure CLI.
3. **Azure SDK for Python**: Install the required Azure SDK libraries.
4. **Environment Variables**: Create a `.env` file with the following variables:
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_CLIENT_SECRET`
   - `LOGGING_CONFIG`=logging-conf.yaml

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/githubofkrishnadhas/azure-decommision-old-snapshots.git
   cd azure-decommision-old-snapshots
    ```
2. Install the required packages:

    ```bash
    poetry install
    ```
3. Set up logging configuration:

   Ensure logging-conf.yaml exists in the root directory or provide a custom path via the LOGGING_CONFIG environment variable.

4. Initiate poetry venv
    ```bash
    poetry shell
    ```
5. Run the script:
    ```python
    poetry run python snapshot.py --subscription_name SUBSCRIPTION_NAME --days DAYS --dry_run
    ```
   
* --dry_run: If specified, the script will only log the snapshots that would be deleted without actually deleting them. This is useful for testing and verification before performing the actual deletion.



## File Structure
* snapshot.py: Main script for identifying and processing old snapshots.
* resourcegraph.py: Contains functions to query Azure Resource Graph for subscriptions and snapshots.
* setup_logging.py: Configures logging for the application.
* README.md: Documentation for the repository.