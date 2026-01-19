import json
import pathlib

# Get the directory where this file (sources.py) is located
CURRENT_DIR = pathlib.Path(__file__).parent

# Path to the sources.json file
SOURCES_FILE = CURRENT_DIR / "sources.json"


def load_sources():
    with open(SOURCES_FILE, "r") as f:
        data = json.load(f)

    # Convert the list of dicts [{"name": "...", "url": "..."}] back to the expected dict format {name: url}
    # used by the rest of the application
    feeds = {}
    for source in data:
        feeds[source["name"]] = source["url"]
    return feeds


PUBLIC_FEEDS = load_sources()
