import os
import argparse
import logging
from setup_logging import setup_logging
from resourcegraph import run_azure_rg_query, run_azure_rg_query_for_snapshots
from utils import convert_list_to_json_file
from dotenv import load_dotenv


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
	older_snapshots = identify_snapshots_older_than_x_days(snapshots=snapshots, days=days)
	logger.info(f"Older snapshot list is {older_snapshots}")
	logger.info(f"Total number of older snapshots is {len(older_snapshots)}")

if __name__ == "__main__":
	main()