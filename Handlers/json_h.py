import json


def read_from_json() -> dict:
    with open("Misc/config.json", 'r') as f:
        data = json.load(f)
    return data


def dump_to_json(key: str, value):
    data = read_from_json()
    data[key] = value
    with open("Misc/config.json", 'w') as f:
        json.dump(data, f, indent=4)
