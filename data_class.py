from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Snapshots:
	name: str
	resource_group: str
	subscription_id: str
	location: str
	sku_name: str
	sku_tier: str
	type: str
	time_created: str
	disk_size_gb: int
	snapshot_source: str
	environment: str
	application_name: str
	complete_tags: Dict[str, Any]
	age_in_days: int

