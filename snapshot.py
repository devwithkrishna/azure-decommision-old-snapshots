import os
import concurrent.futures
import argparse
import logging
from setup_logging import setup_logging
from resourcegraph import run_azure_rg_query, run_azure_rg_query_for_snapshots
from utils import convert_list_to_json_file
from dotenv import load_dotenv
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential

#
# def delete_snapshot(snapshot: dict, dry_run: bool) -> bool:
# 	"""
#
# 	:param snapshot:
# 	:return:
# 	"""
# 	logger = logging.getLogger(__name__)
# 	credential = DefaultAzureCredential()
# 	compute_client = ComputeManagementClient(credential, snapshot['subscription_id'])
# 	snapshot_name = snapshot['name']
# 	resource_group = snapshot['resource_group']
# 	age_in_days = snapshot['age_in_days']
# 	logger.info(f"Starting deletion of snapshot: {snapshot_name} aged {age_in_days} days")
# 	try:
# 		compute_client.snapshots.begin_delete(resource_group, snapshot_name).wait()
# 		logger.info(f"Successfully deleted snapshot: {snapshot_name}")
# 		return True
# 	except Exception as e:
# 		logger.error(f"Failed to delete snapshot {snapshot_name}: {str(e)}")
# 		return False
#
#
# def delete_snapshots_parallel(snapshots: list[dict], max_workers:int, dry_run: bool):
# 	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
# 		future_to_snapshot = {executor.submit(delete_snapshot, snap): snap for snap in snapshots}
#
# 		for future in concurrent.futures.as_completed(future_to_snapshot):
# 			snapshot = future_to_snapshot[future]
# 			try:
# 				result = future.result()
# 				if not result:
# 					logger.warning(f"Retry logic can be applied here for {snapshot['name']}")
# 			except Exception as exc:
# 				logger.exception(f"Unexpected error deleting {snapshot['name']}: {exc}")


def delete_snapshot(snapshot, dry_run: bool):
    """
    Deletes a snapshot or logs the action if dry_run is enabled.

    :param snapshot: The snapshot to delete.
    :param dry_run: If True, only log the action without deleting.
    :return: True if successful or in dry_run mode, False otherwise.
    """
    logger = logging.getLogger(__name__)
    if dry_run:
        logger.info(f"[DRY RUN] Would delete snapshot: {snapshot['name']} aged {snapshot['age_in_days']} days")
        return True

    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, snapshot['subscription_id'])
    snapshot_name = snapshot['name']
    resource_group = snapshot['resource_group']
    age_in_days = snapshot['age_in_days']
    logger.info(f"Starting deletion of snapshot: {snapshot_name} aged {age_in_days} days")
    try:
        compute_client.snapshots.begin_delete(resource_group, snapshot_name).wait()
        logger.info(f"Successfully deleted snapshot: {snapshot_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete snapshot {snapshot_name}: {str(e)}")
        return False


def delete_snapshots_parallel(snapshots: list[dict], max_workers: int, dry_run: bool):
    """
    Deletes snapshots in parallel or logs the actions if dry_run is enabled.

    :param snapshots: List of snapshots to delete.
    :param max_workers: Maximum number of threads for parallel execution.
    :param dry_run: If True, only log the actions without deleting.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_snapshot = {executor.submit(delete_snapshot, snap, dry_run): snap for snap in snapshots}

        for future in concurrent.futures.as_completed(future_to_snapshot):
            snapshot = future_to_snapshot[future]
            try:
                result = future.result()
                if not result and not dry_run:
                    logger.warning(f"Retry logic can be applied here for {snapshot['name']}")
            except Exception as exc:
                logger.exception(f"Unexpected error deleting {snapshot['name']}: {exc}")


def main():
	"""
	main function
	:return:
	"""
	load_dotenv()
	setup_logging()  # Initialize logging
	global logger
	logger = logging.getLogger(__name__)  # Get the logger for this module
	parser = argparse.ArgumentParser(description="Identify Disl Snapshots in Azure older than x days")
	parser.add_argument('--subscription_name', type=str, help='Subscription name to query', required=True)
	parser.add_argument('--days', type=int, help='Number of days to check for snapshots', required=True)
	parser.add_argument('--dry_run', action='store_true', help='Dry run flag')

	args = parser.parse_args()
	subscription_name = args.subscription_name
	days = args.days
	dry_run = args.dry_run

	logger.info(f"Subscription name is {subscription_name}")
	logger.info(f"Days is {days}")
	logger.info(f"Dry run is {dry_run}")


	subscription_ids = run_azure_rg_query(subscription_names=[subscription_name])
	snapshots =run_azure_rg_query_for_snapshots(subscription_ids=subscription_ids, days=days)
	convert_list_to_json_file(data=snapshots, file_name="snapshots.json")
	# older_snapshots = identify_snapshots_older_than_x_days(snapshots=snapshots, days=days)
	logger.info(f"Older snapshot list is {snapshots}")
	logger.info(f"Total number of older snapshots is {len(snapshots)}")
	delete_snapshots_parallel(snapshots=snapshots, max_workers=3, dry_run=dry_run)

if __name__ == "__main__":
	main()