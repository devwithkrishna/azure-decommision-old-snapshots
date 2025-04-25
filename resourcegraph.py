import logging
from azure.identity import DefaultAzureCredential
import azure.mgmt.resourcegraph as arg
from azure.mgmt.resourcegraph.models import QueryRequest
from setup_logging import setup_logging
from dotenv import load_dotenv

def run_azure_rg_query(subscription_names: list[str]):
    """
    Run a resource graph query to get the subscription id of a subscription back
    :return: subscription_id str
    """
    logger = logging.getLogger(__name__)
    credential = DefaultAzureCredential()
    sub_ids= []
    for subscription_name in subscription_names:

        logger.info(f"Credentials for {subscription_name} set....")
        # Create Azure Resource Graph client and set options
        arg_client = arg.ResourceGraphClient(credential)

        query = f"""
                 resourcecontainers 
                 | where type == 'microsoft.resources/subscriptions' and name == '{subscription_name}' 
                 | project subscriptionId 
                """

        # print(f"query is {query}")
        logger.info(f"query is {query}")

        # Create query
        arg_query = arg.models.QueryRequest(query=query)

        # Run query
        arg_result = arg_client.resources(arg_query)

        # Show Python object
        # print(arg_result)
        subscription_id = arg_result.data[0]['subscriptionId']
        logger.info(f"Subscription ID of {subscription_name} is : {subscription_id}")
        sub_ids.append(subscription_id)

    return sub_ids


def run_azure_rg_query_for_snapshots(subscription_ids: list[str], days: int):
    """
    Run a resource graph query to get the snapshots in a subscription older than specified days
    :return: subscription_id str
    """
    logger = logging.getLogger(__name__)
    credential = DefaultAzureCredential()
    # Create Azure Resource Graph client and set options
    arg_client = arg.ResourceGraphClient(credential)
    all_snapshots = []

    query = f"""
            resources
            | where type == "microsoft.compute/snapshots"
            | extend age_in_days = datetime_diff('day', now(), todatetime(properties.timeCreated))
            | where age_in_days >= {days}
            | project name=name, 
              resource_group=resourceGroup,
              subscription_id=subscriptionId, 
              location=location, 
              type=type, 
              sku_name=sku.name, 
              sku_tier=sku.tier, 
              time_created=properties.timeCreated,
              disk_size_gb=properties.diskSizeGB, 
              snapshot_source=properties.creationData.sourceResourceId, 
              environment=tags.Environment, 
              application_name=tags.ApplicationName, 
              complete_tags=tags,
              age_in_days=age_in_days
            """
    logger.info(f"query is {query}")
    skip_token = None

    while True:
        page_size = 100 # number of records per page
        request = QueryRequest(
            subscriptions=subscription_ids,
            query=query,
            options={
                "top": page_size,
                "skipToken": skip_token
            }
        )
        response = arg_client.resources(request)

        all_snapshots.extend(response.data)
        logger.info(f"Fetched {len(response.data)} snapshots from {len(subscription_ids)} subscriptions....")

        if not response.skip_token:
            break  # No more pages
        skip_token = response.skip_token

    return all_snapshots

def main():
    """
    To test the script
    :return:
    """
    load_dotenv()
    setup_logging()  # Initialize logging
    global logger
    logger = logging.getLogger(__name__)  # Get the logger for this module

    logger.info("ARG query being prepared......")
    run_azure_rg_query(subscription_names="TECH-ARCHITECTS-NONPROD")
    logger.info("ARG query Completed......")


if __name__ == "__main__":
    main()