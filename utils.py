import json
from dataclasses import asdict


def convert_list_to_json_file(data, file_name):
	"""
	Converts a list of dictionaries to a JSON file.

	:param data: List of dictionaries to be converted
	:param file_name: Name of the JSON file to save the data
	"""
	if not isinstance(data, list):
		raise ValueError("Input data must be a list of dictionaries.")

	json_data = json.dumps([asdict(s) for s in data])

	with open(file_name, 'w') as json_file:
		json.dump(json_data, json_file, indent=4)


def main():
	"""Test the script"""
	data = [
		{"name": "Alice", "age": 25},
		{"name": "Bob", "age": 30}
	]
	convert_list_to_json_file(data, "output.json")

if __name__ == "__main__":
	main()